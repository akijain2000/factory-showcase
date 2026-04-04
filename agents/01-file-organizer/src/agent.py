"""File organizer: ReAct loop, move_log for rollback, workspace-safe tool dispatch."""

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


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self, *, system: str, messages: List[Dict[str, Any]], tools: Optional[List[str]] = None
    ) -> Any: ...


@dataclass
class AgentConfig:
    root: Path
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 30.0
    system_prompt_path: Optional[Path] = None


@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    move_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)


class FileOrganizerAgent:
    _ALLOWED = frozenset({"list_files", "move_file", "create_directory"})

    def __init__(self, config: AgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tools.items() if k in self._ALLOWED}
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
        path.write_text(
            json.dumps(
                {
                    "state": self._state.name,
                    "session": asdict(self.session),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_state(self, path: Path) -> None:
        d = json.loads(path.read_text(encoding="utf-8"))
        self._state = AgentState[d["state"]]
        s = d["session"]
        self.session = SessionData(
            messages=s["messages"],
            step_num=s["step_num"],
            spent_usd=s["spent_usd"],
            move_log=s["move_log"],
            audit_log=s["audit_log"],
        )

    def _log_step(self, **kw: Any) -> None:
        log.info("%s", json.dumps({"agent": "01-file-organizer", **kw}))

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name, "retryable": False}}
        t0 = time.perf_counter()
        self._goto(AgentState.WAITING_TOOL)
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self.tools[name], args)
                out = fut.result(timeout=self.config.tool_timeout_s)
        except FuturesTimeout:
            self._goto(AgentState.ERROR)
            return {"ok": False, "error": {"code": "TIMEOUT", "message": name, "retryable": True}}
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        self._log_step(step_num=self.session.step_num, state=self._state.name, tool_name=name, elapsed_ms=elapsed_ms)
        self._goto(AgentState.EXECUTING)
        rec = {"ts": time.time(), "tool": name, "args": args, "result_ok": out.get("ok", True)}
        self.session.audit_log.append(rec)
        if name == "move_file" and out.get("ok"):
            self.session.move_log.append({"ts": rec["ts"], "src": args.get("source"), "dest": args.get("destination")})
        return out

    def run(self, user_message: str, llm: LLMClient) -> str:
        t_start = time.time()
        self._goto(AgentState.PLANNING)
        self.session.messages.append({"role": "user", "content": user_message})
        sys_prompt = self.load_system_prompt()
        final = ""
        while self.session.step_num < self.config.max_steps:
            if time.time() - t_start > self.config.max_wall_time_s:
                self._goto(AgentState.DONE)
                return final or "Stopped: wall time limit."
            if self.session.spent_usd >= self.config.max_spend_usd:
                self._goto(AgentState.DONE)
                return final or "Stopped: spend limit."
            self.session.step_num += 1
            turn = llm.complete(system=sys_prompt, messages=list(self.session.messages), tools=list(self._ALLOWED))
            text = getattr(turn, "text", "") or ""
            cost = float(getattr(turn, "cost_usd", 0.0) or 0.0)
            self.session.spent_usd += cost
            calls = getattr(turn, "tool_calls", None) or []
            self.session.messages.append({"role": "assistant", "content": text, "tool_calls": calls})
            self._log_step(step_num=self.session.step_num, state="PLANNING", tool_name=None, elapsed_ms=0)
            final = text
            if not calls:
                self._goto(AgentState.DONE)
                return final
            for c in calls:
                name = c.get("name", "")
                args = c.get("arguments") if isinstance(c.get("arguments"), dict) else {}
                obs = self._call_tool(name, args)
                if not obs.get("ok", True) and not (obs.get("error") or {}).get("retryable"):
                    self._goto(AgentState.ERROR)
                    self.session.messages.append({"role": "user", "content": f"[tool_error]\n{json.dumps(obs)}"})
                    return final + f"\nTool error: {obs}"
                self.session.messages.append({"role": "user", "content": f"[{name}]\n{json.dumps(obs)}"})
            self._goto(AgentState.PLANNING)
        self._goto(AgentState.DONE)
        return final or "Stopped: max steps."


def default_registry(root: Path) -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {"list_files": _stub, "move_file": _stub, "create_directory": _stub}
