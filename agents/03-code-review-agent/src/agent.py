"""
Code Review Supervisor — multi-agent skeleton.

Enforces per–sub-agent tool allowlists when executing handoffs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]

SUBAGENT_TOOLS: Dict[str, FrozenSet[str]] = {
    "security_reviewer": frozenset({"scan_secrets", "check_injection_patterns"}),
    "style_reviewer": frozenset({"lint_style_conventions"}),
    "logic_reviewer": frozenset({"analyze_control_flow"}),
}

SUPERVISOR_TOOLS: FrozenSet[str] = frozenset({"handoff_to_subagent", "merge_findings"})


@dataclass
class CodeReviewConfig:
    max_handoffs: int = 8
    system_prompt_path: Optional[Path] = None


@dataclass
class SupervisorState:
    handoffs_used: int = 0
    pending_findings: List[Dict[str, Any]] = field(default_factory=list)


class CodeReviewSupervisor:
    def __init__(self, config: CodeReviewConfig, tool_impl: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tool_impl = tool_impl
        self.state = SupervisorState()

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def allowed_tools_for(self, role: str) -> FrozenSet[str]:
        if role == "supervisor":
            return SUPERVISOR_TOOLS
        return SUBAGENT_TOOLS.get(role, frozenset())

    def run_supervisor_turn(self, llm_client: Any) -> str:
        raise NotImplementedError("Supervisor ReAct loop + worker scheduling.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    keys: set[str] = set(SUPERVISOR_TOOLS)
    for allowed in SUBAGENT_TOOLS.values():
        keys |= set(allowed)
    return {k: _stub for k in keys}
