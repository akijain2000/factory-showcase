"""Support triage: classify → KB grounding → route per policy → draft or escalate."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, runtime_checkable

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    WAITING_TOOL = auto()
    ERROR = auto()
    DONE = auto()


_TRANSITIONS: Dict[AgentState, frozenset[AgentState]] = {
    AgentState.IDLE: frozenset({AgentState.PLANNING, AgentState.ERROR}),
    AgentState.PLANNING: frozenset(
        {AgentState.EXECUTING, AgentState.WAITING_TOOL, AgentState.DONE, AgentState.ERROR}
    ),
    AgentState.EXECUTING: frozenset({AgentState.PLANNING, AgentState.WAITING_TOOL, AgentState.ERROR}),
    AgentState.WAITING_TOOL: frozenset({AgentState.EXECUTING, AgentState.ERROR}),
    AgentState.ERROR: frozenset({AgentState.DONE}),
    AgentState.DONE: frozenset(),
}

_TOOL_REQ: Dict[str, frozenset[str]] = {
    "classify_intent": frozenset({"ticket_id", "subject", "body"}),
    "search_kb": frozenset({"query"}),
    "route_ticket": frozenset({"ticket_id", "destination", "reason", "priority"}),
    "generate_response": frozenset({"ticket_id", "classification"}),
    "escalate_to_human": frozenset({"ticket_id", "reason", "summary"}),
}
_MUTATING = frozenset({"classify_intent", "route_ticket", "generate_response", "escalate_to_human"})
_ALLOWED = frozenset(_TOOL_REQ.keys())

def _routing_rule(c: Dict[str, Any]) -> tuple[str, bool]:
    cf, pi = float(c.get("confidence", 0) or 0), c.get("primary_intent")
    if pi == "security":
        return "security_queue", True
    if c.get("urgency") == "p1":
        return "incident_bridge", True
    if cf < 0.55 or c.get("needs_human"):
        return "human_triage", True
    if pi == "billing" and cf >= 0.75:
        return "billing_ops", False
    if pi == "how_to" and cf >= 0.7:
        return "success_kb_first", False
    return "human_triage", True

@runtime_checkable
class LLMClient(Protocol):
    def complete(self, *, system: str, messages: List[Dict[str, Any]], tools: Optional[List[str]] = None) -> Any: ...

@dataclass
class SupportTriageAgentConfig:
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 45.0
    system_prompt_path: Optional[Path] = None

@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    last_classification: Optional[Dict[str, Any]] = None
    sla_routing_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    mutation_log: List[Dict[str, Any]] = field(default_factory=list)

class SupportTriageAgent:
    def __init__(self, config: SupportTriageAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tools.items() if k in _ALLOWED}
        self._state = AgentState.IDLE
        self.session = SessionData()

    def _goto(self, nxt: AgentState) -> None:
        if nxt not in _TRANSITIONS[self._state] and nxt != self._state:
            raise RuntimeError(f"invalid transition {self._state} -> {nxt}")
        self._state = nxt

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def save_state(self, path: Path) -> None:
        path.write_text(json.dumps({"state": self._state.name, "session": asdict(self.session)}, indent=2), encoding="utf-8")

    def load_state(self, path: Path) -> None:
        d = json.loads(path.read_text(encoding="utf-8"))
        self._state = AgentState[d["state"]]
        s = d["session"]
        self.session = SessionData(
            messages=s["messages"],
            step_num=s["step_num"],
            spent_usd=s["spent_usd"],
            last_classification=s.get("last_classification"),
            sla_routing_log=s.get("sla_routing_log", []),
            audit_log=s["audit_log"],
            mutation_log=s["mutation_log"],
        )

    def _invoke_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        need = _TOOL_REQ.get(name)
        if not need or not need.issubset(args.keys()):
            return {"ok": False, "error": {"code": "INVALID_INPUT", "retryable": False}}
        if name not in self.tools:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "retryable": False}}
        if name == "route_ticket" and self.session.last_classification:
            dest, _ = _routing_rule(self.session.last_classification)
            if args.get("destination") != dest:
                e = {"code": "ROUTING_MISMATCH", "retryable": True, "expected_destination": dest}
                return {"ok": False, "error": e}
        self._goto(AgentState.WAITING_TOOL)
        t0 = time.perf_counter()
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self.tools[name], args)
                out = fut.result(timeout=self.config.tool_timeout_s)
        except FuturesTimeout:
            self._goto(AgentState.EXECUTING)
            return {"ok": False, "error": {"code": "TIMEOUT", "retryable": True}}
        self._goto(AgentState.EXECUTING)
        log.info("%s", json.dumps({"agent": "10-support-triage", "tool": name, "ms": int((time.perf_counter() - t0) * 1000)}))
        rec = {"ts": time.time(), "tool": name, "args": args, "ok": out.get("ok", True)}
        self.session.audit_log.append(rec)
        if name == "classify_intent" and out.get("ok") and out.get("classification"):
            self.session.last_classification = out["classification"]
        if name in _MUTATING and out.get("ok", True):
            self.session.mutation_log.append(dict(rec, rollback_hint="revert_ticket_mutation"))
        if name == "route_ticket" and out.get("ok", True):
            self.session.sla_routing_log.append(
                {"ts": rec["ts"], "priority": args.get("priority"), "destination": args.get("destination")}
            )
        return out

    def run(self, user_message: str, llm: LLMClient) -> str:
        t0 = time.time()
        self._goto(AgentState.PLANNING)
        self.session.messages.append({"role": "user", "content": user_message})
        system = self.load_system_prompt()
        final = ""
        while self.session.step_num < self.config.max_steps:
            if time.time() - t0 > self.config.max_wall_time_s:
                self._goto(AgentState.DONE)
                return final or "Stopped: wall time limit."
            if self.session.spent_usd >= self.config.max_spend_usd:
                self._goto(AgentState.DONE)
                return final or "Stopped: spend limit."
            self.session.step_num += 1
            turn = llm.complete(system=system, messages=list(self.session.messages), tools=list(_ALLOWED))
            text = getattr(turn, "text", "") or ""
            self.session.spent_usd += float(getattr(turn, "cost_usd", 0.0) or 0.0)
            calls = getattr(turn, "tool_calls", None) or []
            self.session.messages.append({"role": "assistant", "content": text, "tool_calls": calls})
            log.info("%s", json.dumps({"agent": "10-support-triage", "step": self.session.step_num, "phase": "think"}))
            final = text
            if not calls:
                self._goto(AgentState.DONE)
                return final
            self._goto(AgentState.EXECUTING)
            for c in calls:
                name = str(c.get("name", ""))
                raw = c.get("arguments")
                args = raw if isinstance(raw, dict) else {}
                obs = self._invoke_tool(name, args)
                if not obs.get("ok", True) and (obs.get("error") or {}).get("retryable"):
                    if obs.get("error", {}).get("code") == "ROUTING_MISMATCH":
                        args["destination"] = obs["error"]["expected_destination"]
                    obs = self._invoke_tool(name, args)
                self.session.messages.append({"role": "user", "content": f"[observe:{name}]\n{json.dumps(obs)}"})
                if not obs.get("ok", True) and not (obs.get("error") or {}).get("retryable"):
                    self._goto(AgentState.ERROR)
                    return final + f"\nTool error: {obs}"
            self._goto(AgentState.PLANNING)
        self._goto(AgentState.DONE)
        return final or "Stopped: max steps."


def default_registry() -> Dict[str, ToolHandler]:
    stub: ToolHandler = lambda _: {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "retryable": False}}
    return {n: stub for n in _ALLOWED}
