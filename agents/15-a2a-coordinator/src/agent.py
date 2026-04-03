"""
A2A Coordinator Agent — delegation skeleton.

Discover -> negotiate -> delegate -> collect -> resolve.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class A2ACoordinatorConfig:
    agent_directory_uri: str = ""
    message_bus_ref: str = ""
    policy_gate_ref: str = ""
    max_delegation_depth: int = 3
    system_prompt_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "discover_agents",
            "negotiate_protocol",
            "delegate_task",
            "collect_results",
            "resolve_conflicts",
        ]
    )


class A2ACoordinatorAgent:
    def __init__(self, config: A2ACoordinatorConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def _call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.config.tool_allowlist:
            return {"ok": False, "error": {"code": "POLICY_DENY", "message": "tool not allowlisted"}}
        handler = self.tools.get(name)
        if not handler:
            return {"ok": False, "error": {"code": "TOOL_MISSING", "message": name}}
        return handler(args)

    def coordinate(self, task: Dict[str, Any], depth: int = 0, llm_client: Any = None) -> Dict[str, Any]:
        if depth > self.config.max_delegation_depth:
            return {"phase": "depth_exceeded", "error": {"code": "MAX_DEPTH", "message": "delegation depth"}}

        discovered = self._call(
            "discover_agents",
            {
                "required_skills": task.get("required_skills", []),
                "trust_tier_max": task.get("trust_tier_max", "internal"),
                "max_latency_ms": task.get("max_latency_ms", 15000),
            },
        )
        protocol = self._call(
            "negotiate_protocol",
            {
                "peer_agent_ids": [p["agent_id"] for p in discovered.get("agents", [])][:5],
                "payload_schema_ref": task.get("payload_schema_ref"),
                "error_schema_ref": task.get("error_schema_ref"),
            },
        )
        if not protocol.get("ok", True):
            return {"phase": "negotiation_failed", "discovered": discovered, "protocol": protocol}

        delegated = self._call(
            "delegate_task",
            {
                "protocol_id": protocol.get("protocol_id"),
                "subtasks": task.get("subtasks", []),
                "deadline_ms": task.get("deadline_ms", 60000),
            },
        )
        results = self._call(
            "collect_results",
            {
                "task_handles": delegated.get("task_handles", []),
                "wait_policy": task.get("wait_policy", "all_terminal"),
            },
        )
        if results.get("conflicts"):
            resolved = self._call(
                "resolve_conflicts",
                {
                    "conflict_set_id": results.get("conflict_set_id"),
                    "strategy": task.get("conflict_strategy", "evidence_first"),
                },
            )
            return {
                "phase": "resolved",
                "discovered": discovered,
                "protocol": protocol,
                "delegated": delegated,
                "results": results,
                "resolved": resolved,
            }
        return {
            "phase": "completed",
            "discovered": discovered,
            "protocol": protocol,
            "delegated": delegated,
            "results": results,
        }


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {name: _stub for name in A2ACoordinatorConfig().tool_allowlist}
