"""
Migration Planner — plan-and-execute skeleton.

Enforces: plan artifacts exist before execute_step; optional dry_run gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class MigrationConfig:
    allow_execute: bool = False
    max_steps: int = 50
    require_dry_run: bool = True
    system_prompt_path: Optional[Path] = None


@dataclass
class MigrationState:
    current_migration_id: Optional[str] = None
    planned_steps: Set[str] = field(default_factory=set)
    dry_ok: Set[str] = field(default_factory=set)
    executed: Set[str] = field(default_factory=set)


class MigrationPlannerAgent:
    def __init__(self, config: MigrationConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.state = MigrationState()

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def can_execute(self, step_id: str) -> bool:
        if not self.config.allow_execute:
            return False
        if self.config.require_dry_run and step_id not in self.state.dry_ok:
            return False
        return step_id in self.state.planned_steps and step_id not in self.state.executed

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Implement plan-then-execute loop with gates.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    names = (
        "analyze_schema",
        "generate_migration",
        "dry_run",
        "execute_step",
        "rollback_step",
    )
    return {n: _stub for n in names}
