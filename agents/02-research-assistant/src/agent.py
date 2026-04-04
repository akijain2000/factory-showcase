"""Research assistant: ReAct, citations, source memory; per-source retrieval timeout."""

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


_T = {
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
class ResearchAgentConfig:
    memory_store_uri: str
    doc_index_id: str
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 10.0
    max_web_results: int = 5
    system_prompt_path: Optional[Path] = None


@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    citations: List[Dict[str, Any]] = field(default_factory=list)
    move_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)


class ResearchAssistantAgent:
    _TOOLS = frozenset({"web_search", "retrieve_document", "store_memory", "cite_source"})

    def __init__(self, config: ResearchAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tools.items() if k in self._TOOLS}
        self._state = AgentState.IDLE
        self.session = SessionData()

    def _goto(self, n: AgentState) -> None:
        if n != self._state and n not in _T[self._state]:
            raise RuntimeError(f"bad transition {self._state}->{n}")
        self._state = n

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def save_state(self, path: Path) -> None:
        path.write_text(
            json.dumps({"state": self._state.name, "session": asdict(self.session)}, indent=2),
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
            citations=s.get("citations", []),
            move_log=s.get("move_log", []),
            audit_log=s.get("audit_log", []),
        )

    def _log_step(self, **kw: Any) -> None:
        log.info("%s", json.dumps({"agent": "02-research", **kw}))

    def _schema_ok(self, name: str, args: Dict[str, Any]) -> Optional[str]:
        if name == "web_search" and "query" not in args:
            return "missing query"
        if name == "retrieve_document" and "doc_id" not in args and "query" not in args:
            return "need doc_id or query"
        return None

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        bad = self._schema_ok(name, args)
        if bad:
            return {"ok": False, "error": {"code": "BAD_ARGS", "message": bad, "retryable": False}}
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
        rec = {"ts": time.time(), "tool": name, "args": args, "ok": out.get("ok", True)}
        self.session.audit_log.append(rec)
        if name == "cite_source" and out.get("ok"):
            self.session.citations.append(out.get("citation") or args)
        if name == "store_memory" and out.get("ok"):
            self.session.move_log.append({"ts": rec["ts"], "kind": "memory", "ref": args.get("key")})
        return out

    def run(self, user_message: str, llm: LLMClient) -> str:
        t0 = time.time()
        self._goto(AgentState.PLANNING)
        self.session.messages.append({"role": "user", "content": user_message})
        sys_p = self.load_system_prompt()
        final = ""
        while self.session.step_num < self.config.max_steps:
            if time.time() - t0 > self.config.max_wall_time_s or self.session.spent_usd >= self.config.max_spend_usd:
                self._goto(AgentState.DONE)
                return final or "Stopped: budget."
            self.session.step_num += 1
            turn = llm.complete(system=sys_p, messages=list(self.session.messages), tools=list(self._TOOLS))
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
                if n == "web_search" and isinstance(a.get("limit"), int) and a["limit"] > self.config.max_web_results:
                    a = {**a, "limit": self.config.max_web_results}
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

    return {k: _stub for k in ResearchAssistantAgent._TOOLS}
