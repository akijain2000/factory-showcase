"""
Database Admin Agent — safety-critical skeleton.

Implements hard gates: SELECT-only query_db, HITL validation for execute_ddl.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Set


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class DbAdminConfig:
    read_only_sql: bool = True
    allowed_schemas: Optional[Set[str]] = None
    system_prompt_path: Optional[Path] = None


class DbAdminAgent:
    def __init__(self, config: DbAdminConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def validate_query_sql(self, sql: str) -> Optional[str]:
        """Return error code if disallowed."""
        s = sql.strip().lower()
        if self.config.read_only_sql and not s.startswith("select"):
            return "POLICY_DENY"
        return None

    def validate_ddl_request(self, args: Dict[str, Any]) -> Optional[str]:
        if not args.get("approval_id"):
            return "HITL_REQUIRED"
        # Integrate with real HITL service; backup policy checks here.
        return None

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Wire ReAct loop with tool policy enforcement.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "query_db": _stub,
        "explain_query": _stub,
        "backup_table": _stub,
        "execute_ddl": _stub,
    }
