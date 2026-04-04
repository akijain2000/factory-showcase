"""Code review: mandatory scan_secrets, handoff-only scanners, auto merge_findings."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Protocol, runtime_checkable

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]
SUBAGENT_TOOLS: Dict[str, FrozenSet[str]] = {
    "security": frozenset({"scan_secrets", "check_injection_patterns"}),
    "style": frozenset({"lint_style_conventions"}),
    "logic": frozenset({"analyze_control_flow"}),
}
SUP = frozenset({"handoff_to_subagent", "merge_findings"})
_ALL = frozenset().union(*SUBAGENT_TOOLS.values()) | SUP
_SUB = frozenset().union(*SUBAGENT_TOOLS.values())
_RV = frozenset({"security", "style", "logic"})


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
class CodeReviewConfig:
    max_handoffs: int = 8
    max_steps: int = 20
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 1.0
    tool_timeout_s: float = 45.0
    max_files: int = 50
    system_prompt_path: Optional[Path] = None


@dataclass
class SessionData:
    messages: List[Dict[str, Any]] = field(default_factory=list)
    step_num: int = 0
    spent_usd: float = 0.0
    handoffs: int = 0
    secrets_done: bool = False
    reviewers_done: FrozenSet[str] = frozenset()
    findings_batches: List[Any] = field(default_factory=list)
    move_log: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

class CodeReviewSupervisor:
    def __init__(self, config: CodeReviewConfig, tool_impl: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = {k: v for k, v in tool_impl.items() if k in _ALL}
        self._state = AgentState.IDLE
        self.session = SessionData()

    def _goto(self, n: AgentState) -> None:
        if n != self._state and n not in _T[self._state]:
            raise RuntimeError(f"bad transition {self._state}->{n}")
        self._state = n

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def allowed_tools_for(self, role: str) -> FrozenSet[str]:
        return SUP if role == "supervisor" else SUBAGENT_TOOLS.get(role, frozenset())

    def save_state(self, path: Path) -> None:
        d = asdict(self.session)
        d["reviewers_done"] = list(self.session.reviewers_done)
        path.write_text(json.dumps({"state": self._state.name, "session": d}, indent=2), encoding="utf-8")

    def load_state(self, path: Path) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._state = AgentState[raw["state"]]
        s = raw["session"]
        self.session = SessionData(
            messages=s["messages"],
            step_num=s["step_num"],
            spent_usd=s["spent_usd"],
            handoffs=s.get("handoffs", 0),
            secrets_done=s.get("secrets_done", False),
            reviewers_done=frozenset(s.get("reviewers_done", [])),
            findings_batches=s.get("findings_batches", []),
            move_log=s.get("move_log", []),
            audit_log=s.get("audit_log", []),
        )

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
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
        log.info("%s", json.dumps({"agent": "03-code-review", "step": self.session.step_num, "tool": name,
            "ms": int((time.perf_counter() - t0) * 1000)}))
        self._goto(AgentState.EXECUTING)
        self.session.audit_log.append({"ts": time.time(), "tool": name, "args": args})
        if name == "handoff_to_subagent":
            self.session.move_log.append({"tool": name, "reviewer": args.get("reviewer")})
            self.session.handoffs += 1
            rv = args.get("reviewer")
            if rv in _RV:
                self.session.reviewers_done |= {rv}
                if isinstance(out.get("findings"), list):
                    self.session.findings_batches.append(out["findings"])
        return out

    def run(self, user_message: str, llm: LLMClient) -> str:
        t0, final = time.time(), ""
        self._goto(AgentState.PLANNING)
        self.session.messages.append({"role": "user", "content": user_message})
        if not self.session.secrets_done:
            sec = self._call_tool("scan_secrets", {"diff_text": user_message})
            self.session.messages.append({"role": "user", "content": f"[scan_secrets]\n{json.dumps(sec)}"})
            self.session.secrets_done = True
            self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        while self.session.step_num < self.config.max_steps:
            if time.time() - t0 > self.config.max_wall_time_s or self.session.spent_usd >= self.config.max_spend_usd:
                self._goto(AgentState.DONE)
                return final or "Stopped: budget."
            self.session.step_num += 1
            turn = llm.complete(system=sys_p, messages=list(self.session.messages), tools=list(_ALL))
            text = getattr(turn, "text", "") or ""
            self.session.spent_usd += float(getattr(turn, "cost_usd", 0.0) or 0.0)
            calls = list(getattr(turn, "tool_calls", None) or [])
            if self.session.handoffs >= self.config.max_handoffs:
                calls = [c for c in calls if c.get("name") != "handoff_to_subagent"]
            if self.session.reviewers_done >= _RV and not any(c.get("name") == "merge_findings" for c in calls):
                calls.append({"name": "merge_findings", "arguments": {"findings": self.session.findings_batches}})
            self.session.messages.append({"role": "assistant", "content": text, "tool_calls": calls})
            final = text
            if not calls:
                self._goto(AgentState.DONE)
                return final
            for c in calls:
                n, a = c.get("name", ""), c.get("arguments") if isinstance(c.get("arguments"), dict) else {}
                if n == "handoff_to_subagent":
                    if len(a.get("files") or []) > self.config.max_files:
                        self._goto(AgentState.ERROR)
                        return "Too many files; split the diff."
                    rv = a.get("reviewer", "")
                    obs = (
                        self._call_tool(n, a)
                        if rv in SUBAGENT_TOOLS
                        else {"ok": False, "error": {"code": "BAD_REVIEWER", "message": rv, "retryable": False}}
                    )
                elif n in _SUB:
                    obs = {"ok": False, "error": {"code": "POLICY", "message": "use handoff_to_subagent", "retryable": False}}
                else:
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

    return {k: _stub for k in _ALL}
