"""
Context Engineer Agent — ACE loop skeleton.

Curate -> evaluate -> (optional) reflect -> compress -> evolve system prompt under policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class ContextEngineerConfig:
    context_store_uri: str = ""
    max_tokens: int = 120_000
    pre_compress_ratio: float = 0.85
    system_prompt_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "curate_context",
            "reflect_on_output",
            "compress_context",
            "update_system_prompt",
            "evaluate_context_quality",
        ]
    )


class ContextEngineerAgent:
    def __init__(self, config: ContextEngineerConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def run_loop(
        self,
        user_message: str,
        raw_artifacts: List[Dict[str, Any]],
        llm_client: Any,
    ) -> Dict[str, Any]:
        """
        Reference control flow — replace llm_client with your host integration.
        """
        curated = self._call(
            "curate_context",
            {
                "objective": user_message,
                "raw_artifacts": raw_artifacts,
                "max_items": 64,
            },
        )
        quality = self._call(
            "evaluate_context_quality",
            {"curated_bundle_id": curated.get("bundle_id"), "objective": user_message},
        )
        if not quality.get("ok", True):
            return {"phase": "quality_gate", "quality": quality, "curated": curated}

        reflection = self._call(
            "reflect_on_output",
            {
                "task_objective": user_message,
                "model_output": "",
                "success_criteria": [],
            },
        )

        est_tokens = int(quality.get("estimated_tokens", 0))
        if est_tokens > int(self.config.max_tokens * self.config.pre_compress_ratio):
            compressed = self._call(
                "compress_context",
                {
                    "bundle_id": curated.get("bundle_id"),
                    "target_tokens": int(self.config.max_tokens * 0.7),
                    "preserve_tags": ["safety", "tool_contract", "error_trace"],
                },
            )
            return {"phase": "compressed", "curated": curated, "compressed": compressed, "reflection": reflection}

        return {"phase": "ready", "curated": curated, "reflection": reflection, "quality": quality}


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {name: _stub for name in ContextEngineerConfig().tool_allowlist}
