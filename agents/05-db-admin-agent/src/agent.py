"""DB admin copilot: SELECT gate, HITL approval for execute_ddl, explain/backup hooks."""

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
_TOOLS = frozenset({"query_db", "explain_query", "backup_table", "execute_ddl"})


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
class DbAdminConfig:
    read_only_sql: bool = True
    allowed_schemas: Optional[Set[str]] = None
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 30.0
    require_backup_before_ddl: bool = False
    system_prompt_path: Optional[Path] = None
@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    approval_id: Optional[str] = None
    last_backup_id: Optional[str] = None
    move_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)
class DbAdminAgent:
    def __init__(self, config: DbAdminConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tools.items() if k in _TOOLS}
        self._state = AgentState.IDLE
        self.session = SessionData()

    def _goto(self, n: AgentState) -> None:
        if n != self._state and n not in _T[self._state]:
            raise RuntimeError(f"bad transition {self._state}->{n}")
        self._state = n

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def validate_query_sql(self, sql: str) -> Optional[str]:
        s = sql.strip().lower()
        if self.config.read_only_sql and not s.startswith("select"):
            return "POLICY_DENY"
        return None

    def validate_ddl_request(self, args: Dict[str, Any]) -> Optional[str]:
        if not args.get("approval_id"):
            return "HITL_REQUIRED"
        if self.config.require_backup_before_ddl and not (args.get("backup_id") or self.session.last_backup_id):
            return "BACKUP_REQUIRED"
        return None

    def save_state(self, path: Path) -> None:
        path.write_text(json.dumps({"state": self._state.name, "session": asdict(self.session)}, indent=2), encoding="utf-8")

    def load_state(self, path: Path) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._state = AgentState[raw["state"]]
        s = raw["session"]
        self.session = SessionData(
            messages=s["messages"],
            step_num=s["step_num"],
            spent_usd=s["spent_usd"],
            approval_id=s.get("approval_id"),
            last_backup_id=s.get("last_backup_id"),
            move_log=s.get("move_log", []),
            audit_log=s.get("audit_log", []),
        )

    def _log_step(self, **kw: Any) -> None:
        log.info("%s", json.dumps({"agent": "05-db-admin", **kw}))

    def _precheck(self, name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if name == "query_db":
            sql = args.get("sql") or ""
            code = self.validate_query_sql(sql)
            if code:
                return {"ok": False, "error": {"code": code, "message": "query not allowed", "retryable": False}}
        if name == "execute_ddl":
            err = self.validate_ddl_request(args)
            if err:
                return {"ok": False, "error": {"code": err, "message": "approval or backup", "retryable": False}}
        return None

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "execute_ddl":
            args = {
                **args,
                "approval_id": args.get("approval_id") or self.session.approval_id,
                "backup_id": args.get("backup_id") or self.session.last_backup_id,
            }
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
        self.session.audit_log.append({"ts": time.time(), "tool": name, "args_keys": list(args.keys())})
        if (out.get("error") or {}).get("code") in ("POLICY_DENY", "HITL_REQUIRED"):
            self._goto(AgentState.ERROR)
        if out.get("hitl_approved") and out.get("approval_id"):
            self.session.approval_id = str(out["approval_id"])
        if name == "backup_table" and out.get("ok") and out.get("backup_id"):
            self.session.last_backup_id = str(out["backup_id"])
        if name == "execute_ddl" and out.get("ok"):
            self.session.move_log.append({"tool": name, "ts": time.time(), "idempotency_key": args.get("idempotency_key")})
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
            turn = llm.complete(system=sys_p, messages=list(self.session.messages), tools=list(_TOOLS))
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
                self.session.messages.append({"role": "user", "content": f"[{n}]\n{json.dumps(obs)}"})
                ec = (obs.get("error") or {}).get("code")
                if ec in ("POLICY_DENY", "HITL_REQUIRED"):
                    self._goto(AgentState.DONE)
                    return final + f"\nStopped: {ec}"
                if not obs.get("ok", True) and not (obs.get("error") or {}).get("retryable"):
                    self._goto(AgentState.ERROR)
                    return final + f"\n{obs}"
            self._goto(AgentState.PLANNING)
        self._goto(AgentState.DONE)
        return final or "max steps"


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {n: _stub for n in _TOOLS}
