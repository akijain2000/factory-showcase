"""
Skeleton orchestration for support-triage agent.
Enforce routing rules in code or via validated tool backend.
"""

from __future__ import annotations

from typing import Any, TypedDict


class Classification(TypedDict, total=False):
    primary_intent: str
    secondary_intents: list[str]
    urgency: str
    sentiment: str
    confidence: float
    entities: dict[str, str | None]
    routing_hint: str
    needs_human: bool


def classify_intent(ticket_id: str, subject: str, body: str, channel: str | None = None) -> dict[str, Any]:
    raise NotImplementedError


def search_kb(query: str, locale: str | None = None, top_k: int = 5) -> dict[str, Any]:
    raise NotImplementedError


def route_ticket(ticket_id: str, destination: str, reason: str, priority: str) -> dict[str, Any]:
    raise NotImplementedError


def generate_response(
    ticket_id: str,
    classification: Classification,
    tone: str | None = None,
    kb_article_ids: list[str] | None = None,
) -> dict[str, Any]:
    raise NotImplementedError


def escalate_to_human(ticket_id: str, reason: str, summary: str, severity: str | None = None) -> dict[str, Any]:
    raise NotImplementedError


def decide_route(c: Classification) -> tuple[str, bool]:
    """
    Return (destination, requires_escalation).
    Mirror system-prompt routing rules for deterministic tests.
    """
    if c.get("primary_intent") == "security":
        return "security_queue", True
    if c.get("urgency") == "p1":
        return "incident_bridge", True
    if c.get("confidence", 0) < 0.55 or c.get("needs_human"):
        return "human_triage", True
    if c.get("primary_intent") == "billing" and c.get("confidence", 0) >= 0.75:
        return "billing_ops", False
    if c.get("primary_intent") == "how_to" and c.get("confidence", 0) >= 0.7:
        return "success_kb_first", False
    return "human_triage", True


def handle_ticket(ticket_id: str, subject: str, body: str) -> str:
    """Skeleton: classify → KB? → route → respond or escalate. Implement LLM + tools."""
    raise NotImplementedError
