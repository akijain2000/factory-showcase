"""Cost optimizer — estimate → budget → route → downgrade; post-flight token tracking."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    WAITING_TOOL = auto()
    ERROR = auto()
    DONE = auto()


_COST_TRANS = frozenset({
    (AgentState.IDLE, AgentState.PLANNING), (AgentState.IDLE, AgentState.EXECUTING), (AgentState.PLANNING, AgentState.EXECUTING),
    (AgentState.EXECUTING, AgentState.WAITING_TOOL), (AgentState.WAITING_TOOL, AgentState.EXECUTING), (AgentState.WAITING_TOOL, AgentState.ERROR),
    (AgentState.EXECUTING, AgentState.DONE), (AgentState.EXECUTING, AgentState.ERROR), (AgentState.ERROR, AgentState.DONE),
})


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class CircuitLimits:
    max_steps: int = 32
    max_wall_time_s: float = 60.0
    max_spend_usd: float = 25.0
    tool_timeout_s: float = 20.0


@dataclass
class CostOptimizerConfig:
    budget_ledger_uri: str = ""
    route_table_ref: str = ""
    circuit_breaker_policy_ref: str = ""
    system_prompt_path: Optional[Path] = None
    limits: CircuitLimits = field(default_factory=CircuitLimits)
    persistence_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: ["route_to_model", "track_tokens", "check_budget", "downgrade_model", "estimate_cost"]
    )


class CostOptimizerAgent:
    def __init__(self, config: CostOptimizerConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.state, self._step, self._t0, self._spend_usd = AgentState.IDLE, 0, 0.0, 0.0
        self.audit_log: List[Dict[str, Any]] = []
        self._pool = ThreadPoolExecutor(max_workers=2)

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def _goto(self, new: AgentState, reason: str = "") -> None:
        if new != self.state and (self.state, new) not in _COST_TRANS:
            raise RuntimeError(f"invalid transition {self.state}->{new}")
        prev, self.state = self.state, new
        self.audit_log.append({"kind": "state", "from": prev.name, "to": new.name, "reason": reason, "ts": time.time()})
        log.info("structured", extra=self.audit_log[-1])

    def _breaker(self) -> Optional[str]:
        if self._step >= self.config.limits.max_steps:
            return "max_steps"
        if self._t0 and time.monotonic() - self._t0 > self.config.limits.max_wall_time_s:
            return "max_wall_time_s"
        if self._spend_usd >= self.config.limits.max_spend_usd:
            return "max_spend_usd"
        return None

    def _tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.config.tool_allowlist:
            return {"ok": False, "error": {"code": "POLICY_DENY", "message": "deny", "retryable": False}}
        h = self.tools.get(name)
        if not h:
            return {"ok": False, "error": {"code": "TOOL_MISSING", "message": name, "retryable": False}}
        self._goto(AgentState.WAITING_TOOL, name)
        self._step += 1
        brk = self._breaker()
        if brk:
            self._goto(AgentState.ERROR, brk)
            return {"ok": False, "error": {"code": "CIRCUIT", "message": brk, "retryable": False}}
        to = self.config.limits.tool_timeout_s
        for attempt in range(2):
            fut = self._pool.submit(h, args)
            try:
                out = fut.result(timeout=to)
            except FuturesTimeout:
                fut.cancel()
                out = {"ok": False, "error": {"code": "TIMEOUT", "message": name, "retryable": True}}
            self._spend_usd += float((out or {}).get("cost_usd") or 0)
            self.audit_log.append({"kind": "tool", "name": name, "ok": out.get("ok", True), "ts": time.time()})
            log.info("structured", extra=self.audit_log[-1])
            if out.get("ok", True):
                self._goto(AgentState.EXECUTING, "ok")
                return out
            if (out.get("error") or {}).get("retryable") and attempt == 0:
                continue
            self._goto(AgentState.ERROR, name)
            return out
        return {"ok": False, "error": {"code": "INTERNAL", "message": name, "retryable": False}}

    def save_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.persistence_path or Path(__file__).resolve().parent / "agent_state.json"
        blob = {"state": self.state.name, "step": self._step, "spend_usd": self._spend_usd, "audit_tail": self.audit_log[-200:]}
        p.write_text(json.dumps(blob), encoding="utf-8")

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.persistence_path or Path(__file__).resolve().parent / "agent_state.json"
        if not p.exists():
            return
        d = json.loads(p.read_text(encoding="utf-8"))
        self.state, self._step, self._spend_usd = AgentState[d["state"]], int(d.get("step", 0)), float(d.get("spend_usd", 0))
        self.audit_log = list(d.get("audit_tail", []))

    def preflight(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if self._t0 == 0.0:
            self._t0 = time.monotonic()
        if self.state == AgentState.IDLE:
            self._goto(AgentState.EXECUTING, "preflight_entry")
        est = self._tool(
            "estimate_cost",
            {
                "task_class": request.get("task_class", "general"),
                "input_tokens_est": request.get("input_tokens_est", 0),
                "output_tokens_est": request.get("output_tokens_est", 0),
                "candidate_models": request.get("candidate_models", []),
            },
        )
        budget = self._tool("check_budget", {"scope": request.get("scope", {}), "projected_increment_usd": est.get("min_usd", 0)})
        if budget.get("action") == "halt":
            return {"phase": "halted", "estimate": est, "budget": budget}
        route = self._tool(
            "route_to_model",
            {
                "task_class": request.get("task_class"),
                "latency_slo_ms": request.get("latency_slo_ms", 8000),
                "quality_band": request.get("quality_band", "standard"),
                "budget_hint_usd": est.get("min_usd"),
            },
        )
        if budget.get("action") == "downgrade":
            route = self._tool(
                "downgrade_model",
                {"from_model": route.get("model_id"), "reason": "BUDGET_PRESSURE", "max_relative_quality_loss": 0.15},
            )
        return {"phase": "routed", "estimate": est, "budget": budget, "route": route}

    def run(self, request: Dict[str, Any], llm_client: Optional[LLMClient] = None) -> Dict[str, Any]:
        self._t0, self._step = time.monotonic(), 0
        self._goto(AgentState.PLANNING, "cost_run")
        if llm_client:
            llm_client.complete([{"role": "user", "content": "Summarize routing constraints."}])
        self._goto(AgentState.EXECUTING, "preflight")
        body = self.preflight(request)
        if body.get("phase") == "halted":
            self._goto(AgentState.DONE, "halt")
            return {**body, "audit": self.audit_log}
        track = self._tool(
            "track_tokens",
            {
                "request_id": request.get("request_id", ""), "model_id": (body.get("route") or {}).get("model_id"),
                "input_tokens": request.get("actual_input_tokens"), "output_tokens": request.get("actual_output_tokens"),
            },
        )
        self._goto(AgentState.DONE, "tracked")
        return {**body, "track_tokens": track, "audit": self.audit_log}


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in CostOptimizerConfig().tool_allowlist}
