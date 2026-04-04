"""A2A coordinator — discover → negotiate → delegate → collect → resolve."""

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


_A2A_TRANS = frozenset({
    (AgentState.IDLE, AgentState.PLANNING), (AgentState.IDLE, AgentState.DONE), (AgentState.IDLE, AgentState.EXECUTING),
    (AgentState.PLANNING, AgentState.EXECUTING), (AgentState.EXECUTING, AgentState.WAITING_TOOL),
    (AgentState.WAITING_TOOL, AgentState.EXECUTING), (AgentState.WAITING_TOOL, AgentState.ERROR),
    (AgentState.EXECUTING, AgentState.DONE), (AgentState.EXECUTING, AgentState.ERROR), (AgentState.ERROR, AgentState.DONE),
})


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class CircuitLimits:
    max_steps: int = 56
    max_wall_time_s: float = 180.0
    max_spend_usd: float = 50.0
    tool_timeout_s: float = 45.0


@dataclass
class A2ACoordinatorConfig:
    agent_directory_uri: str = ""
    message_bus_ref: str = ""
    policy_gate_ref: str = ""
    max_delegation_depth: int = 3
    system_prompt_path: Optional[Path] = None
    limits: CircuitLimits = field(default_factory=CircuitLimits)
    persistence_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "discover_agents", "negotiate_protocol", "delegate_task", "collect_results", "resolve_conflicts",
        ]
    )


class A2ACoordinatorAgent:
    def __init__(self, config: A2ACoordinatorConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.state, self._step, self._t0, self._spend_usd = AgentState.IDLE, 0, 0.0, 0.0
        self.audit_log: List[Dict[str, Any]] = []
        self._pool = ThreadPoolExecutor(max_workers=2)

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def _goto(self, new: AgentState, reason: str = "") -> None:
        if new != self.state and (self.state, new) not in _A2A_TRANS:
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

    def run(self, task: Dict[str, Any], depth: int = 0, llm_client: Optional[LLMClient] = None) -> Dict[str, Any]:
        self._t0, self._step = time.monotonic(), 0
        if depth > self.config.max_delegation_depth:
            self._goto(AgentState.DONE, "depth")
            return {"phase": "depth_exceeded", "error": {"code": "MAX_DEPTH", "message": "delegation depth"}, "audit": self.audit_log}
        self._goto(AgentState.PLANNING, "coordinate")
        if llm_client:
            llm_client.complete([{"role": "user", "content": "Decompose; map peer capabilities."}])
        self._goto(AgentState.EXECUTING, "flow")
        discovered = self._tool(
            "discover_agents",
            {
                "required_skills": task.get("required_skills", []),
                "trust_tier_max": task.get("trust_tier_max", "internal"),
                "max_latency_ms": task.get("max_latency_ms", 15000),
            },
        )
        protocol = self._tool(
            "negotiate_protocol",
            {
                "peer_agent_ids": [p["agent_id"] for p in discovered.get("agents", [])][:5],
                "payload_schema_ref": task.get("payload_schema_ref"),
                "error_schema_ref": task.get("error_schema_ref"),
            },
        )
        if not protocol.get("ok", True):
            self._goto(AgentState.DONE, "negotiation_fail")
            return {"phase": "negotiation_failed", "discovered": discovered, "protocol": protocol, "audit": self.audit_log}
        delegated = self._tool(
            "delegate_task",
            {
                "protocol_id": protocol.get("protocol_id"),
                "subtasks": task.get("subtasks", []),
                "deadline_ms": task.get("deadline_ms", 60000),
                "timeout_ms": task.get("timeout_ms", task.get("deadline_ms", 60000)),
            },
        )
        results = self._tool(
            "collect_results",
            {"task_handles": delegated.get("task_handles", []), "wait_policy": task.get("wait_policy", "all_terminal")},
        )
        if results.get("conflicts"):
            resolved = self._tool(
                "resolve_conflicts",
                {"conflict_set_id": results.get("conflict_set_id"), "strategy": task.get("conflict_strategy", "evidence_first")},
            )
            self._goto(AgentState.DONE, "resolved")
            return {
                "phase": "resolved", "discovered": discovered, "protocol": protocol, "delegated": delegated,
                "results": results, "resolved": resolved, "audit": self.audit_log,
            }
        self._goto(AgentState.DONE, "complete")
        return {"phase": "completed", "discovered": discovered, "protocol": protocol, "delegated": delegated, "results": results, "audit": self.audit_log}

    def coordinate(self, task: Dict[str, Any], depth: int = 0, llm_client: Any = None) -> Dict[str, Any]:
        return self.run(task, depth, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in A2ACoordinatorConfig().tool_allowlist}
