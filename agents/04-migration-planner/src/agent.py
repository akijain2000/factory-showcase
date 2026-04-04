"""Migration planner: plan-then-execute; dry_run gate; rollback_step audit trail."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, runtime_checkable

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]
_NAMES = frozenset(
    {"analyze_schema", "generate_migration", "dry_run", "execute_step", "rollback_step"}
)
class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    WAITING_TOOL = auto()
    ERROR = auto()
    DONE = auto()


_T = {
    AgentState.IDLE: frozenset({AgentState.PLANNING}),
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
    def complete(self, *, system: str, messages: List[Dict[str, Any]], tools: Optional[List[str]] = None) -> Any: ...

@dataclass
class MigrationConfig:
    allow_execute: bool = False
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 60.0
    require_dry_run: bool = True
    system_prompt_path: Optional[Path] = None

@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    plan_committed: bool = False
    planned_steps: Set[str] = field(default_factory=set)
    dry_ok: Set[str] = field(default_factory=set)
    executed: Set[str] = field(default_factory=set)
    move_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

class MigrationPlannerAgent:
    def __init__(self, config: MigrationConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tools.items() if k in _NAMES}
        self._state = AgentState.IDLE
        self.session = SessionData()

    def _goto(self, n: AgentState) -> None:
        if n != self._state and n not in _T[self._state]:
            raise RuntimeError(f"bad transition {self._state}->{n}")
        self._state = n

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def can_execute(self, step_id: str) -> bool:
        if not self.config.allow_execute:
            return False
        if self.config.require_dry_run and step_id not in self.session.dry_ok:
            return False
        return step_id in self.session.planned_steps and step_id not in self.session.executed

    def save_state(self, path: Path) -> None:
        d = asdict(self.session)
        for k in ("planned_steps", "dry_ok", "executed"):
            d[k] = list(self.session.__dict__[k])
        path.write_text(json.dumps({"state": self._state.name, "session": d}, indent=2), encoding="utf-8")

    def load_state(self, path: Path) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._state = AgentState[raw["state"]]
        s = raw["session"]
        self.session = SessionData(
            messages=s["messages"],
            step_num=s["step_num"],
            spent_usd=s["spent_usd"],
            plan_committed=s.get("plan_committed", False),
            planned_steps=set(s.get("planned_steps", [])),
            dry_ok=set(s.get("dry_ok", [])),
            executed=set(s.get("executed", [])),
            move_log=s.get("move_log", []),
            audit_log=s.get("audit_log", []),
        )

    def _log_step(self, **kw: Any) -> None:
        log.info("%s", json.dumps({"agent": "04-migration", **kw}))

    def _precheck(self, name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if name == "execute_step":
            if not self.session.plan_committed:
                return {"ok": False, "error": {"code": "NO_PLAN", "message": "generate_migration first", "retryable": False}}
            sid = args.get("step_id", "")
            if not self.can_execute(sid):
                return {"ok": False, "error": {"code": "GATE", "message": sid, "retryable": False}}
        if name in ("dry_run", "rollback_step") and not args.get("step_id"):
            return {"ok": False, "error": {"code": "BAD_ARGS", "message": "step_id", "retryable": False}}
        return None

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        pre = self._precheck(name, args)
        if pre:
            return pre
        if name not in self.tools:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name, "retryable": False}}
        self._goto(AgentState.WAITING_TOOL)
        t0 = time.perf_counter()
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                out = ex.submit(self.tools[name], args).result(timeout=self.config.tool_timeout_s)
        except FuturesTimeout:
            self._goto(AgentState.ERROR)
            return {"ok": False, "error": {"code": "TIMEOUT", "message": name, "retryable": True}}
        self._log_step(
            step_num=self.session.step_num,
            state=self._state.name,
            tool_name=name,
            elapsed_ms=int((time.perf_counter() - t0) * 1000),
        )
        self._goto(AgentState.EXECUTING)
        self.session.audit_log.append({"ts": time.time(), "tool": name, "args": args, "ok": out.get("ok", True)})
        if out.get("ok", True):
            if name == "generate_migration":
                self.session.plan_committed = True
                for sid in out.get("step_ids") or []:
                    self.session.planned_steps.add(str(sid))
            elif name == "dry_run" and args.get("step_id"):
                self.session.dry_ok.add(str(args["step_id"]))
            elif name == "execute_step" and args.get("step_id"):
                sid = str(args["step_id"])
                self.session.executed.add(sid)
                self.session.move_log.append({"kind": "execute", "step_id": sid, "ts": time.time()})
            elif name == "rollback_step" and args.get("step_id"):
                self.session.move_log.append({"kind": "rollback", "step_id": str(args["step_id"]), "ts": time.time()})
        return out

    def run(self, user_message: str, llm: LLMClient) -> str:
        t0, final = time.time(), ""
        self._goto(AgentState.PLANNING)
        self.session.messages.append({"role": "user", "content": user_message})
        sys_p = self.load_system_prompt()
        while self.session.step_num < self.config.max_steps:
            if time.time() - t0 > self.config.max_wall_time_s or self.session.spent_usd >= self.config.max_spend_usd:
                self._goto(AgentState.DONE)
                return final or "Stopped: budget."
            self.session.step_num += 1
            turn = llm.complete(system=sys_p, messages=list(self.session.messages), tools=list(_NAMES))
            text = getattr(turn, "text", "") or ""
            self.session.spent_usd += float(getattr(turn, "cost_usd", 0.0) or 0.0)
            calls = list(getattr(turn, "tool_calls", None) or [])
            self.session.messages.append({"role": "assistant", "content": text, "tool_calls": calls})
            self._log_step(step_num=self.session.step_num, state="PLANNING", tool_name=None, elapsed_ms=0)
            final = text
            if not calls:
                self._goto(AgentState.DONE)
                return final
            for c in calls:
                n, a = c.get("name", ""), c.get("arguments") if isinstance(c.get("arguments"), dict) else {}
                obs = self._call_tool(n, a)
                if not obs.get("ok", True) and not (obs.get("error") or {}).get("retryable"):
                    self._goto(AgentState.ERROR)
                    return final + f"\n{obs}"
                self.session.messages.append({"role": "user", "content": f"[{n}]\n{json.dumps(obs)}"})
            self._goto(AgentState.PLANNING)
        self._goto(AgentState.DONE)
        return final or "max steps"


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in _NAMES}
