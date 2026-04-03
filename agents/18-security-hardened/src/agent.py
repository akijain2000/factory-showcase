"""
Security-Hardened Agent — defense-in-depth wrapper (stub).

Enforces sanitize → inject scan → permission check around an inner agent,
then validates outputs and writes audit records.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class SecurityAgentConfig:
    policy_bundle_ref: Optional[str] = None
    audit_sink_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None


class SecurityHardenedAgent:
    def __init__(self, config: SecurityAgentConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def gated_inner_turn(
        self,
        user_text: str,
        correlation_id: str,
        inner: Callable[[str], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Example gate ordering for integrators."""
        san = self.tool("sanitize_input", {"text": user_text, "profile": "markdown"})
        inj = self.tool("detect_injection", {"text": san.get("sanitized_text", "")})
        if inj.get("action") == "block":
            self.tool(
                "audit_log",
                {
                    "event_type": "injection_detected",
                    "severity": inj.get("severity", "high"),
                    "correlation_id": correlation_id,
                    "details": {"verdict": inj.get("verdict")},
                },
            )
            return {"blocked": True, "reason": "injection", "inj": inj}
        draft = inner(str(san.get("sanitized_text", "")))
        val = self.tool("validate_output", draft.get("validation_request", {}))
        return {"blocked": False, "draft": draft, "validation": val}

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Wire inner agent + tool registry to your runtime.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "sanitize_input": _stub,
        "validate_output": _stub,
        "detect_injection": _stub,
        "check_permissions": _stub,
        "audit_log": _stub,
    }
