"""
Streaming Pipeline Agent — event path skeleton.

Emit -> interceptor chain -> aggregate -> consumer; cancel_subtree for scoped teardown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class StreamingPipelineConfig:
    event_bus_endpoint: str = ""
    root_scope_id: str = "root"
    system_prompt_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "emit_event",
            "register_interceptor",
            "cancel_subtree",
            "aggregate_stream",
            "inspect_backpressure",
        ]
    )


class StreamingPipelineAgent:
    def __init__(self, config: StreamingPipelineConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def run_loop(self, incident: Dict[str, Any], llm_client: Any) -> Dict[str, Any]:
        """
        Reference flow for diagnosing lag + scoped cancel. Replace llm_client with host integration.
        """
        bp = self._call(
            "inspect_backpressure",
            {
                "consumer_group": incident.get("consumer_group", "default"),
                "topics": incident.get("topics", []),
                "sample_limit": 5,
            },
        )
        if not bp.get("ok", True):
            return {"phase": "backpressure_read_failed", "backpressure": bp}

        if bp.get("lag_max_seconds", 0) > incident.get("cancel_if_lag_over_s", 1e9):
            cancel = self._call(
                "cancel_subtree",
                {
                    "scope_id": incident.get("scope_id", self.config.root_scope_id),
                    "reason_code": "LAG_POLICY",
                    "grace_ms": incident.get("grace_ms", 2000),
                    "propagate_to": "children",
                },
            )
            return {"phase": "cancelled_subtree", "backpressure": bp, "cancel": cancel}

        return {"phase": "observed", "backpressure": bp}


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {name: _stub for name in StreamingPipelineConfig().tool_allowlist}
