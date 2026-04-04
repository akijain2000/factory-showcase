"""Docs maintainer: diff-first drift detection, narrow reads, patch via update_doc, link checks."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import asdict, dataclass, field
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
    "read_source": frozenset({"path"}),
    "diff_changes": frozenset({"base", "head"}),
    "update_doc": frozenset({"path", "patch", "rationale"}),
    "check_links": frozenset({"paths"}),
    "search_codebase": frozenset({"query"}),
}
_MUTATING = frozenset({"update_doc"})
_ALLOWED = frozenset(_TOOL_REQ.keys())


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self, *, system: str, messages: List[Dict[str, Any]], tools: Optional[List[str]] = None
    ) -> Any: ...


@dataclass
class DocsMaintainerAgentConfig:
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 90.0
    system_prompt_path: Optional[Path] = None


@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    last_diff_key: Optional[str] = None
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
    mutation_log: List[Dict[str, Any]] = field(default_factory=list)


class DocsMaintainerAgent:
    def __init__(self, config: DocsMaintainerAgentConfig, tools: Dict[str, ToolHandler]) -> None:
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
            last_diff_key=s.get("last_diff_key"),
            audit_log=s["audit_log"],
            mutation_log=s["mutation_log"],
        )

    def _log_step(self, **kw: Any) -> None:
        log.info("%s", json.dumps({"agent": "09-docs-maintainer", **kw}))

    def _validate(self, name: str, args: Dict[str, Any]) -> Optional[str]:
        need = _TOOL_REQ.get(name)
        if not need or not need.issubset(args.keys()):
            return "INVALID_INPUT"
        if name == "update_doc" and len(str(args.get("rationale", ""))) < 8:
            return "RATIONALE_REQUIRED"
        return None

    def _invoke_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        err = self._validate(name, args)
        if err:
            return {"ok": False, "error": {"code": err, "retryable": False}}
        if name not in self.tools:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "retryable": False}}
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
        self._log_step(tool=name, ms=int((time.perf_counter() - t0) * 1000))
        rec = {"ts": time.time(), "tool": name, "args": args, "ok": out.get("ok", True)}
        self.session.audit_log.append(rec)
        if name == "diff_changes" and out.get("ok"):
            self.session.last_diff_key = f"{args.get('base')}..{args.get('head')}"
        if name in _MUTATING and out.get("ok", True):
            self.session.mutation_log.append(
                dict(rec, rollback_hint="revert_patch", pre_image=out.get("previous_content"))
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
            self._log_step(step=self.session.step_num, phase="think")
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
                    obs = self._invoke_tool(name, args)
                self.session.messages.append({"role": "user", "content": f"[observe:{name}]\n{json.dumps(obs)}"})
                if not obs.get("ok", True) and not (obs.get("error") or {}).get("retryable"):
                    self._goto(AgentState.ERROR)
                    return final + f"\nTool error: {obs}"
            self._goto(AgentState.PLANNING)
        self._goto(AgentState.DONE)
        return final or "Stopped: max steps."


def default_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "retryable": False}}

    return {n: _stub for n in _ALLOWED}
