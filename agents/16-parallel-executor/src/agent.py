"""Parallel Executor — fan-out/fan-in, trace aggregation, partial failure."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    WAITING_TOOL = auto()
    ERROR = auto()
    DONE = auto()


def _allowed() -> Dict[AgentState, tuple]:
    return {
        AgentState.IDLE: (AgentState.PLANNING, AgentState.ERROR),
        AgentState.PLANNING: (AgentState.EXECUTING, AgentState.ERROR, AgentState.DONE),
        AgentState.EXECUTING: (AgentState.WAITING_TOOL, AgentState.ERROR, AgentState.DONE),
        AgentState.WAITING_TOOL: (AgentState.EXECUTING, AgentState.ERROR, AgentState.DONE),
        AgentState.ERROR: (AgentState.DONE,),
        AgentState.DONE: (AgentState.IDLE,),
    }


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class ParallelExecutorConfig:
    default_concurrency: int = 16
    system_prompt_path: Optional[Path] = None
    trace_store_ref: Optional[str] = None
    max_steps: int = 64
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 5.0
    tool_timeout_s: float = 30.0
    state_path: Optional[Path] = None


class ParallelExecutorAgent:
    def __init__(self, config: ParallelExecutorConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.agent_state = AgentState.IDLE
        self.correlation_id = ""
        self.merge_strategy = "concat"
        self.audit: List[Dict[str, Any]] = []
        self._step = 0
        self._t0 = 0.0
        self._spend = 0.0
        self._pool = ThreadPoolExecutor(max_workers=8)
        self._trans = _allowed()

    def _goto(self, n: AgentState) -> None:
        if n not in self._trans.get(self.agent_state, ()):
            raise RuntimeError(f"bad transition {self.agent_state!r} -> {n!r}")
        self.audit.append({"ts": time.time(), "kind": "transition", "to": n.name})
        log.info("agent_transition", extra={"to": n.name})
        self.agent_state = n

    def _breakers(self) -> Optional[str]:
        if self._step >= self.config.max_steps:
            return "max_steps"
        if time.monotonic() - self._t0 > self.config.max_wall_time_s:
            return "max_wall_time"
        if self._spend >= self.config.max_spend_usd:
            return "max_spend"
        return None

    def _dispatch(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        trip = self._breakers()
        if trip:
            self._goto(AgentState.ERROR)
            return {"ok": False, "error": {"code": "CIRCUIT", "message": trip, "retryable": False}}
        self._goto(AgentState.WAITING_TOOL)
        self._step += 1
        h = self.tools.get(name)
        if not h:
            self._goto(AgentState.EXECUTING)
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name, "retryable": False}}
        fut = self._pool.submit(h, args)
        try:
            out = fut.result(timeout=self.config.tool_timeout_s)
        except FutTimeout:
            fut.cancel()
            self.audit.append({"ts": time.time(), "kind": "tool_timeout", "tool": name})
            self._goto(AgentState.EXECUTING)
            return {"ok": False, "error": {"code": "TIMEOUT", "message": name, "retryable": True}}
        if isinstance(out, dict) and out.get("cost_usd") is not None:
            self._spend += float(out["cost_usd"])
        self.audit.append({"ts": time.time(), "kind": "tool", "tool": name, "ok": out.get("ok", True)})
        err = out.get("error") if isinstance(out, dict) else None
        if isinstance(err, dict) and err.get("retryable") and self._step < self.config.max_steps:
            return self._dispatch(name, args)
        self._goto(AgentState.EXECUTING)
        return out

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        h = self.tools.get(name)
        if not h:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name}}
        return h(args)

    def save_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        p.write_text(
            json.dumps(
                {
                    "agent_state": self.agent_state.name,
                    "correlation_id": self.correlation_id,
                    "merge_strategy": self.merge_strategy,
                    "step": self._step,
                    "spend": self._spend,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        if not p.is_file():
            return
        d = json.loads(p.read_text(encoding="utf-8"))
        self.agent_state = AgentState[d["agent_state"]]
        self.correlation_id = d.get("correlation_id", "")
        self.merge_strategy = d.get("merge_strategy", "concat")
        self._step = int(d.get("step", 0))
        self._spend = float(d.get("spend", 0.0))

    def run(self, user_message: str, llm: LLMClient) -> str:
        self.agent_state, self._step, self._spend, self._t0 = AgentState.IDLE, 0, 0.0, time.monotonic()
        self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        raw = llm.complete(sys_p, f"Return JSON array of {{id,payload}} shards for: {user_message[:1800]}")
        try:
            shards = json.loads(raw) if raw.strip().startswith("[") else []
        except json.JSONDecodeError:
            shards = []
        if not shards:
            lines = user_message.splitlines()[:8] or [user_message]
            shards = [{"id": f"s{i}", "payload": x} for i, x in enumerate(lines)]
        self.correlation_id = f"corr-{int(time.time() * 1000)}"
        trip = self._breakers()
        if trip:
            self._goto(AgentState.ERROR)
            return json.dumps({"error": trip})
        self._goto(AgentState.EXECUTING)
        self._dispatch("set_concurrency_limit", {"limit": self.config.default_concurrency})
        fo = self._dispatch(
            "fan_out",
            {"correlation_id": self.correlation_id, "shards": shards, "merge_strategy": self.merge_strategy},
        )
        tr = self._dispatch("trace_aggregate", {"correlation_id": self.correlation_id, "fan_out": fo})
        partial = bool(tr.get("failed") or tr.get("errors"))
        pol = "continue_with_partial"
        if partial:
            pf = self._dispatch(
                "handle_partial_failure",
                {"correlation_id": self.correlation_id, "trace": tr, "policy_candidates": ["continue_with_partial", "abort_merge"]},
            )
            pol = pf.get("policy", pol)
            if pol == "abort_merge":
                self._goto(AgentState.DONE)
                return json.dumps({"aborted": True, "trace": tr})
        fi = self._dispatch(
            "fan_in",
            {"correlation_id": self.correlation_id, "merge_strategy": self.merge_strategy, "trace": tr, "fan_out": fo},
        )
        self._goto(AgentState.DONE)
        return llm.complete(sys_p, f"Merge summary. policy={pol}\n{json.dumps(fi)[:3500]}")

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        return self.run(user_message, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {k: _stub for k in ("fan_out", "fan_in", "trace_aggregate", "handle_partial_failure", "set_concurrency_limit")}
