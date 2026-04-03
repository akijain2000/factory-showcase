"""
Workflow Orchestrator Agent — DAG execution loop (stub).

Schedules steps in topological order, checkpoints state, evaluates branch
conditions, and resumes after failures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class WorkflowConfig:
    checkpoint_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None


@dataclass
class RunContext:
    run_id: str
    dag_id: str
    revision: int
    completed: Set[str] = field(default_factory=set)
    outputs: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestratorAgent:
    def __init__(self, config: WorkflowConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        handler = self.tools.get(name)
        if handler is None:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name}}
        return handler(args)

    def plan_ready_steps(self, layers: List[List[str]], ctx: RunContext) -> List[str]:
        """Return ready steps in the earliest incomplete layer (illustrative)."""
        for layer in layers:
            pending = [s for s in layer if s not in ctx.completed]
            if pending:
                return pending
        return []

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Implement planner + DAG tool loop with your runtime.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "define_dag": _stub,
        "execute_step": _stub,
        "checkpoint_state": _stub,
        "resume_from_checkpoint": _stub,
        "evaluate_condition": _stub,
    }
