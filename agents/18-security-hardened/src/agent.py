"""Security-hardened agent — validate, scan, permission gates, output validation, audit."""

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


_TRANS = {
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
class SecurityAgentConfig:
    policy_bundle_ref: Optional[str] = None
    audit_sink_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None
    principal: str = "user:session"
    max_steps: int = 48
    max_wall_time_s: float = 90.0
    max_spend_usd: float = 3.0
    tool_timeout_s: float = 25.0
    state_path: Optional[Path] = None


class SecurityHardenedAgent:
    def __init__(self, config: SecurityAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.agent_state = AgentState.IDLE
        self.audit: List[Dict[str, Any]] = []
        self._step = 0
        self._t0 = 0.0
        self._spend = 0.0
        self._pool = ThreadPoolExecutor(max_workers=4)

    def _goto(self, n: AgentState) -> None:
        if n not in _TRANS.get(self.agent_state, ()):
            raise RuntimeError(f"bad transition {self.agent_state!r} -> {n!r}")
        self.audit.append({"ts": time.time(), "kind": "transition", "to": n.name})
        log.info("security_agent", extra={"state": n.name})
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
        self.audit.append({"ts": time.time(), "kind": "mutation", "tool": name, "payload_keys": list(args.keys())})
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
            json.dumps({"agent_state": self.agent_state.name, "step": self._step, "spend": self._spend}, indent=2),
            encoding="utf-8",
        )

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        if not p.is_file():
            return
        d = json.loads(p.read_text(encoding="utf-8"))
        self.agent_state = AgentState[d["agent_state"]]
        self._step = int(d.get("step", 0))
        self._spend = float(d.get("spend", 0.0))

    def run(self, user_message: str, llm: LLMClient) -> str:
        self.agent_state, self._step, self._spend, self._t0 = AgentState.IDLE, 0, 0.0, time.monotonic()
        self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        self._goto(AgentState.EXECUTING)
        san = self._dispatch("sanitize_input", {"text": user_message, "profile": "markdown", "policy_ref": self.config.policy_bundle_ref})
        st = san.get("sanitized_text", user_message)
        inj = self._dispatch("detect_injection", {"text": st})
        if inj.get("action") == "block" or inj.get("severity") == "high":
            self._dispatch(
                "audit_log",
                {"event_type": "injection_detected", "severity": inj.get("severity", "high"), "details": inj},
            )
            self._goto(AgentState.DONE)
            return json.dumps({"reason_code": "DENY_INJECTION", "safe_next_step": "shorten or rephrase input"})
        plan = llm.complete(sys_p, f"Propose one JSON object {{tool,args}} for this sanitized request: {st[:2000]}")
        try:
            act = json.loads(plan) if "{" in plan else {}
        except json.JSONDecodeError:
            act = {}
        tool_n, targs = act.get("tool"), act.get("args") or {}
        if tool_n:
            perm = self._dispatch(
                "check_permissions",
                {"principal": self.config.principal, "tool": tool_n, "resource_scope": targs.get("scope", "*")},
            )
            if perm.get("verdict") != "allow":
                self._dispatch("audit_log", {"event_type": "deny", "tool": tool_n, "perm": perm})
                self._goto(AgentState.DONE)
                return json.dumps({"reason_code": "DENY_PERMISSION", "details": perm})
            self._dispatch(tool_n, targs)
            self._dispatch("audit_log", {"event_type": "tool_executed", "tool": tool_n})
        draft = {"text": llm.complete(sys_p, f"Answer safely for: {st[:2500]}"), "validation_request": {"schema": "plain_text"}}
        val = self._dispatch("validate_output", draft.get("validation_request", {}))
        if not val.get("ok", True):
            self._dispatch("audit_log", {"event_type": "validation_fail", "errors": val.get("errors")})
        self._dispatch("audit_log", {"event_type": "turn_complete", "audit_sink_ref": self.config.audit_sink_ref})
        self._goto(AgentState.DONE)
        return json.dumps({"answer": draft.get("text"), "reason_code": "ALLOW", "validation": val})

    def gated_inner_turn(self, user_text: str, correlation_id: str, inner: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
        san = self.tool("sanitize_input", {"text": user_text, "profile": "markdown"})
        inj = self.tool("detect_injection", {"text": san.get("sanitized_text", "")})
        if inj.get("action") == "block":
            self.tool("audit_log", {"event_type": "injection_detected", "correlation_id": correlation_id, "details": inj})
            return {"blocked": True, "reason": "injection", "inj": inj}
        draft = inner(str(san.get("sanitized_text", "")))
        val = self.tool("validate_output", draft.get("validation_request", {}))
        return {"blocked": False, "draft": draft, "validation": val}

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        return self.run(user_message, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {k: _stub for k in ("sanitize_input", "validate_output", "detect_injection", "check_permissions", "audit_log")}
