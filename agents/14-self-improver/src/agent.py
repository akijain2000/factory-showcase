"""Self-improver — Karpathy loop: read → edit → evaluate → compare → commit."""

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


_K_TRANS = frozenset({
    (AgentState.IDLE, AgentState.PLANNING), (AgentState.PLANNING, AgentState.EXECUTING), (AgentState.EXECUTING, AgentState.WAITING_TOOL),
    (AgentState.WAITING_TOOL, AgentState.EXECUTING), (AgentState.WAITING_TOOL, AgentState.ERROR), (AgentState.EXECUTING, AgentState.DONE),
    (AgentState.EXECUTING, AgentState.ERROR), (AgentState.ERROR, AgentState.DONE),
})


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class CircuitLimits:
    max_steps: int = 40
    max_wall_time_s: float = 3600.0
    max_spend_usd: float = 100.0
    tool_timeout_s: float = 120.0


@dataclass
class SelfImproverConfig:
    prompt_registry_uri: str = ""
    eval_suite_ref: str = ""
    metrics_store_uri: str = ""
    system_prompt_path: Optional[Path] = None
    limits: CircuitLimits = field(default_factory=CircuitLimits)
    persistence_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "read_current_prompt", "edit_prompt", "run_evaluation", "compare_metrics", "commit_or_revert",
        ]
    )


class SelfImproverAgent:
    def __init__(self, config: SelfImproverConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.state, self._step, self._t0, self._spend_usd = AgentState.IDLE, 0, 0.0, 0.0
        self.audit_log: List[Dict[str, Any]] = []
        self._pool = ThreadPoolExecutor(max_workers=2)

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def _goto(self, new: AgentState, reason: str = "") -> None:
        if new != self.state and (self.state, new) not in _K_TRANS:
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

    def run(self, job: Dict[str, Any], llm_client: Optional[LLMClient] = None) -> Dict[str, Any]:
        self._t0, self._step = time.monotonic(), 0
        self._goto(AgentState.PLANNING, "karpathy")
        if llm_client:
            llm_client.complete([{"role": "user", "content": f"Hypothesis for prompt {job.get('prompt_id')}"}])
        self._goto(AgentState.EXECUTING, "loop")
        current = self._tool("read_current_prompt", {"prompt_id": job.get("prompt_id"), "namespace": job.get("namespace", "default")})
        edited = self._tool(
            "edit_prompt",
            {
                "prompt_id": job.get("prompt_id"),
                "parent_hash": current.get("content_hash"),
                "diff_unified": job.get("diff_unified", ""),
                "rationale": job.get("rationale", ""),
            },
        )
        if not edited.get("ok", True):
            self._goto(AgentState.DONE, "edit_fail")
            return {"phase": "edit_failed", "current": current, "edited": edited, "audit": self.audit_log}
        cand = edited.get("candidate_id")
        ev = self._tool(
            "run_evaluation",
            {"suite_version": job.get("suite_version"), "prompt_candidate_id": cand, "random_seed": job.get("random_seed", 42)},
        )
        cmp_ = self._tool(
            "compare_metrics",
            {
                "baseline_run_id": job.get("baseline_run_id"),
                "candidate_run_id": ev.get("run_id"),
                "suite_version": job.get("suite_version"),
            },
        )
        decision = "keep" if cmp_.get("gates_pass") is True else "discard"
        final = self._tool(
            "commit_or_revert",
            {"prompt_id": job.get("prompt_id"), "candidate_id": cand, "decision": decision, "evidence": {"compare": cmp_, "eval": ev}},
        )
        self._goto(AgentState.DONE, "committed")
        return {"phase": "completed", "current": current, "edited": edited, "eval": ev, "compare": cmp_, "final": final, "audit": self.audit_log}

    def improvement_loop(self, job: Dict[str, Any], llm_client: Any = None) -> Dict[str, Any]:
        return self.run(job, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in SelfImproverConfig().tool_allowlist}
