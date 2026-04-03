"""
Skeleton runtime for the learning-tutor agent.
Wire tool handlers to your LLM function-calling or MCP host.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class TutorConfig:
    learner_id: str
    default_topic_depth: Literal["quick", "standard", "deep"] = "standard"


def assess_knowledge(learner_id: str, topic: str, depth: str = "standard") -> dict[str, Any]:
    """Delegate to assess_knowledge tool implementation."""
    raise NotImplementedError


def generate_exercise(
    learner_id: str,
    topic: str,
    difficulty: float,
    format_: str | None = None,
    avoid_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Delegate to generate_exercise tool implementation."""
    raise NotImplementedError


def store_progress(
    learner_id: str,
    topic: str,
    outcome: str,
    exercise_id: str | None = None,
    hints_used: int | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Delegate to store_progress tool implementation."""
    raise NotImplementedError


def recall_history(
    learner_id: str,
    topic: str | None = None,
    mode: str = "both",
    limit: int = 20,
) -> dict[str, Any]:
    """Delegate to recall_history tool implementation."""
    raise NotImplementedError


def run_turn(config: TutorConfig, user_message: str) -> str:
    """Skeleton: call LLM with tools; return assistant message."""
    raise NotImplementedError
