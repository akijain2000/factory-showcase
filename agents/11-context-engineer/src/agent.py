"""Context Engineer — ACE: curate → evaluate → reflect → compress → prompt evolution."""

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


_ACE_TRANS = frozenset({
    (AgentState.IDLE, AgentState.PLANNING), (AgentState.PLANNING, AgentState.EXECUTING), (AgentState.EXECUTING, AgentState.WAITING_TOOL),
    (AgentState.WAITING_TOOL, AgentState.EXECUTING), (AgentState.WAITING_TOOL, AgentState.ERROR), (AgentState.EXECUTING, AgentState.DONE),
    (AgentState.EXECUTING, AgentState.ERROR), (AgentState.ERROR, AgentState.DONE),
})


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class CircuitLimits:
    max_steps: int = 64
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 10.0
    tool_timeout_s: float = 30.0


@dataclass
class ContextEngineerConfig:
    context_store_uri: str = ""
    max_tokens: int = 120_000
    pre_compress_ratio: float = 0.85
    system_prompt_path: Optional[Path] = None
    limits: CircuitLimits = field(default_factory=CircuitLimits)
    persistence_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "curate_context", "reflect_on_output", "compress_context", "update_system_prompt", "evaluate_context_quality",
        ]
    )


class ContextEngineerAgent:
    def __init__(self, config: ContextEngineerConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.state, self._step, self._t0, self._spend_usd = AgentState.IDLE, 0, 0.0, 0.0
        self.audit_log: List[Dict[str, Any]] = []
        self._pool = ThreadPoolExecutor(max_workers=2)

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def _goto(self, new: AgentState, reason: str = "") -> None:
        if new != self.state and (self.state, new) not in _ACE_TRANS:
            raise RuntimeError(f"invalid transition {self.state}->{new}")
        prev, self.state = self.state, new
        self.audit_log.append({"kind": "state", "from": prev.name, "to": new.name, "reason": reason, "ts": time.time()})
        log.info("structured", extra=self.audit_log[-1])

    def _breaker(self) -> Optional[str]:
        if self._step >= self.config.limits.max_steps:
            return "max_steps"
        if time.monotonic() - self._t0 > self.config.limits.max_wall_time_s:
            return "max_wall_time_s"
        if self._spend_usd >= self.config.limits.max_spend_usd:
            return "max_spend_usd"
        return None

    def _tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.config.tool_allowlist:
            return {"ok": False, "error": {"code": "POLICY_DENY", "message": "tool not allowlisted", "retryable": False}}
        h = self.tools.get(name)
        if not h:
            return {"ok": False, "error": {"code": "TOOL_MISSING", "message": name, "retryable": False}}
        self._goto(AgentState.WAITING_TOOL, name)
        self._step += 1
        br = self._breaker()
        if br:
            self._goto(AgentState.ERROR, br)
            return {"ok": False, "error": {"code": "CIRCUIT", "message": br, "retryable": False}}
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
                self._goto(AgentState.EXECUTING, "tool_ok")
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

    def run(self, user_message: str, raw_artifacts: List[Dict[str, Any]], llm_client: Optional[LLMClient] = None) -> Dict[str, Any]:
        self._t0, self._step = time.monotonic(), 0
        self._goto(AgentState.PLANNING, "ace_start")
        if llm_client:
            llm_client.complete([{"role": "user", "content": f"Plan ACE phases for: {user_message[:500]}"}])
        self._goto(AgentState.EXECUTING, "plan_done")
        curated = self._tool("curate_context", {"objective": user_message, "raw_artifacts": raw_artifacts, "max_items": 64})
        if not curated.get("ok", True):
            self._goto(AgentState.DONE, "curate_fail")
            return {"phase": "error", "curated": curated, "audit": self.audit_log}
        quality = self._tool(
            "evaluate_context_quality", {"curated_bundle_id": curated.get("bundle_id"), "objective": user_message},
        )
        if not quality.get("ok", True):
            self._goto(AgentState.DONE, "quality_gate")
            return {"phase": "quality_gate", "curated": curated, "quality": quality, "audit": self.audit_log}
        reflect = self._tool(
            "reflect_on_output", {"task_objective": user_message, "model_output": "", "success_criteria": []},
        )
        est = int(quality.get("estimated_tokens", 0))
        compressed = None
        if est > int(self.config.max_tokens * self.config.pre_compress_ratio):
            compressed = self._tool(
                "compress_context",
                {
                    "bundle_id": curated.get("bundle_id"),
                    "target_tokens": int(self.config.max_tokens * 0.7),
                    "preserve_tags": ["safety", "tool_contract", "error_trace"],
                },
            )
        prompt_upd = self._tool(
            "update_system_prompt",
            {"change_rationale": "ace_windowing", "diff_unified": "", "parent_version": quality.get("version"), "dry_run": True},
        )
        self._goto(AgentState.DONE, "ace_complete")
        return {
            "phase": "ready", "curated": curated, "quality": quality, "reflection": reflect, "compressed": compressed,
            "prompt_dry_run": prompt_upd, "audit": self.audit_log,
        }

    def run_loop(self, user_message: str, raw_artifacts: List[Dict[str, Any]], llm_client: Any = None) -> Dict[str, Any]:
        return self.run(user_message, raw_artifacts, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in ContextEngineerConfig().tool_allowlist}
