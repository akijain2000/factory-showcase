"""Streaming pipeline — events, backpressure, interceptors, aggregation."""

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


_STREAM_TRANS = frozenset({
    (AgentState.IDLE, AgentState.PLANNING), (AgentState.PLANNING, AgentState.EXECUTING), (AgentState.EXECUTING, AgentState.WAITING_TOOL),
    (AgentState.WAITING_TOOL, AgentState.EXECUTING), (AgentState.WAITING_TOOL, AgentState.ERROR), (AgentState.EXECUTING, AgentState.DONE),
    (AgentState.EXECUTING, AgentState.ERROR), (AgentState.ERROR, AgentState.DONE),
})


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, messages: List[Dict[str, str]], **kwargs: Any) -> str: ...


@dataclass
class CircuitLimits:
    max_steps: int = 48
    max_wall_time_s: float = 90.0
    max_spend_usd: float = 5.0
    tool_timeout_s: float = 25.0


@dataclass
class StreamingPipelineConfig:
    event_bus_endpoint: str = ""
    root_scope_id: str = "root"
    system_prompt_path: Optional[Path] = None
    limits: CircuitLimits = field(default_factory=CircuitLimits)
    persistence_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "emit_event", "register_interceptor", "cancel_subtree", "aggregate_stream", "inspect_backpressure",
        ]
    )


class StreamingPipelineAgent:
    def __init__(self, config: StreamingPipelineConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.state, self._step, self._t0, self._spend_usd = AgentState.IDLE, 0, 0.0, 0.0
        self.audit_log: List[Dict[str, Any]] = []
        self._pool = ThreadPoolExecutor(max_workers=2)

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def _goto(self, new: AgentState, reason: str = "") -> None:
        if new != self.state and (self.state, new) not in _STREAM_TRANS:
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

    def run(self, incident: Dict[str, Any], llm_client: Optional[LLMClient] = None) -> Dict[str, Any]:
        self._t0, self._step = time.monotonic(), 0
        self._goto(AgentState.PLANNING, "pipeline")
        if llm_client:
            llm_client.complete([{"role": "user", "content": json.dumps({"incident": incident})[:1500]}])
        self._goto(AgentState.EXECUTING, "plan")
        bp = self._tool(
            "inspect_backpressure",
            {"consumer_group": incident.get("consumer_group", "default"), "topics": incident.get("topics", []), "sample_limit": 5},
        )
        if not bp.get("ok", True):
            self._goto(AgentState.DONE, "bp_fail")
            return {"phase": "backpressure_read_failed", "backpressure": bp, "audit": self.audit_log}
        if bp.get("lag_max_seconds", 0) > incident.get("cancel_if_lag_over_s", 1e9):
            cancel = self._tool(
                "cancel_subtree",
                {
                    "scope_id": incident.get("scope_id", self.config.root_scope_id),
                    "reason_code": "LAG_POLICY",
                    "grace_ms": incident.get("grace_ms", 2000),
                    "propagate_to": "children",
                },
            )
            self._goto(AgentState.DONE, "cancelled")
            return {"phase": "cancelled_subtree", "backpressure": bp, "cancel": cancel, "audit": self.audit_log}
        reg = self._tool(
            "register_interceptor",
            {
                "scope_id": incident.get("scope_id", self.config.root_scope_id),
                "phase": "ingress",
                "order_key": incident.get("order_key", "default"),
            },
        )
        emit = self._tool(
            "emit_event",
            {
                "topic": incident.get("topic", "ops.health"),
                "partition_key": incident.get("partition_key", "singleton"),
                "schema_version": incident.get("schema_version", "1"),
                "causation_id": incident.get("causation_id", ""),
                "payload": {"backpressure": bp},
            },
        )
        agg = self._tool(
            "aggregate_stream",
            {"topics": incident.get("topics", []), "window": incident.get("window", "tumbling"), "late_data": incident.get("late_data", "drop")},
        )
        self._goto(AgentState.DONE, "observed")
        return {
            "phase": "observed", "backpressure": bp, "interceptor": reg, "emit": emit, "aggregate": agg, "audit": self.audit_log,
        }

    def run_loop(self, incident: Dict[str, Any], llm_client: Any = None) -> Dict[str, Any]:
        return self.run(incident, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in StreamingPipelineConfig().tool_allowlist}
