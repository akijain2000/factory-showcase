"""
File Organizer Agent — skeleton orchestrator.

Loads system instructions from ../system-prompt.md and dispatches
registered tools (list_files, move_file, create_directory).
Replace the LLM client with your provider SDK.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class AgentConfig:
    root: Path
    max_steps: int = 20
    system_prompt_path: Optional[Path] = None


@dataclass
class AgentState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    step: int = 0


class FileOrganizerAgent:
    def __init__(self, config: AgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.state = AgentState()

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        """Single ReAct step: append user msg, call LLM, execute tool calls if any."""
        raise NotImplementedError("Wire your model client + tool loop here.")


def default_registry(root: Path) -> Dict[str, ToolHandler]:
    """Placeholder handlers — replace with real FS operations bounded by root."""

    def _not_implemented(args: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "list_files": _not_implemented,
        "move_file": _not_implemented,
        "create_directory": _not_implemented,
    }
