"""
Eval Agent — adaptive rubric generation, scoring, and calibration (stub).

Implements a thin orchestration shell; wire tools to your evaluation service.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class EvalAgentConfig:
    rubric_registry_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None


class EvalAgent:
    def __init__(self, config: EvalAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.active_rubric_id: Optional[str] = None

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

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        """
        Expected control flow:

        1. Parse evaluation request (batch vs single).
        2. generate_rubric or load rubric by id.
        3. For each trajectory: optional filter_by_dimension → score_trajectory.
        4. calibrate_rubric when anchors provided.
        5. aggregate_scores for cohort summary.
        """
        raise NotImplementedError("Implement tool loop with your model host.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "generate_rubric": _stub,
        "score_trajectory": _stub,
        "filter_by_dimension": _stub,
        "aggregate_scores": _stub,
        "calibrate_rubric": _stub,
    }
