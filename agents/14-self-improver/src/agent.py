"""
Self-Improver Agent — Karpathy loop skeleton.

Read -> edit -> evaluate -> compare -> commit_or_revert.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class SelfImproverConfig:
    prompt_registry_uri: str = ""
    eval_suite_ref: str = ""
    metrics_store_uri: str = ""
    system_prompt_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "read_current_prompt",
            "edit_prompt",
            "run_evaluation",
            "compare_metrics",
            "commit_or_revert",
        ]
    )


class SelfImproverAgent:
    def __init__(self, config: SelfImproverConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def improvement_loop(self, job: Dict[str, Any], llm_client: Any) -> Dict[str, Any]:
        """
        Reference harness — host supplies evaluation runner and registry backing.
        """
        current = self._call(
            "read_current_prompt",
            {"prompt_id": job.get("prompt_id"), "namespace": job.get("namespace", "default")},
        )
        edited = self._call(
            "edit_prompt",
            {
                "prompt_id": job.get("prompt_id"),
                "parent_hash": current.get("content_hash"),
                "diff_unified": job.get("diff_unified", ""),
                "rationale": job.get("rationale", ""),
            },
        )
        if not edited.get("ok", True):
            return {"phase": "edit_failed", "current": current, "edited": edited}

        candidate_id = edited.get("candidate_id")
        eval_run = self._call(
            "run_evaluation",
            {
                "suite_version": job.get("suite_version"),
                "prompt_candidate_id": candidate_id,
                "random_seed": job.get("random_seed", 42),
            },
        )
        comparison = self._call(
            "compare_metrics",
            {
                "baseline_run_id": job.get("baseline_run_id"),
                "candidate_run_id": eval_run.get("run_id"),
                "suite_version": job.get("suite_version"),
            },
        )
        decision = "discard"
        if comparison.get("gates_pass") is True:
            decision = "keep"
        final = self._call(
            "commit_or_revert",
            {
                "prompt_id": job.get("prompt_id"),
                "candidate_id": candidate_id,
                "decision": decision,
                "evidence": {"compare": comparison, "eval": eval_run},
            },
        )
        return {
            "phase": "completed",
            "current": current,
            "edited": edited,
            "eval": eval_run,
            "compare": comparison,
            "final": final,
        }


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {name: _stub for name in SelfImproverConfig().tool_allowlist}
