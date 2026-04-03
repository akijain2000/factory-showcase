"""
Cost Optimizer Agent — budget-aware routing skeleton.

estimate_cost -> check_budget -> route_to_model -> track_tokens; downgrade_model on pressure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class CostOptimizerConfig:
    budget_ledger_uri: str = ""
    route_table_ref: str = ""
    circuit_breaker_policy_ref: str = ""
    system_prompt_path: Optional[Path] = None
    tool_allowlist: List[str] = field(
        default_factory=lambda: [
            "route_to_model",
            "track_tokens",
            "check_budget",
            "downgrade_model",
            "estimate_cost",
        ]
    )


class CostOptimizerAgent:
    def __init__(self, config: CostOptimizerConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def preflight(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        est = self._call(
            "estimate_cost",
            {
                "task_class": request.get("task_class", "general"),
                "input_tokens_est": request.get("input_tokens_est", 0),
                "output_tokens_est": request.get("output_tokens_est", 0),
                "candidate_models": request.get("candidate_models", []),
            },
        )
        budget = self._call(
            "check_budget",
            {
                "scope": request.get("scope", {}),
                "projected_increment_usd": est.get("min_usd", 0),
            },
        )
        if budget.get("action") == "halt":
            return {"phase": "halted", "estimate": est, "budget": budget}

        route = self._call(
            "route_to_model",
            {
                "task_class": request.get("task_class"),
                "latency_slo_ms": request.get("latency_slo_ms", 8000),
                "quality_band": request.get("quality_band", "standard"),
                "budget_hint_usd": est.get("min_usd"),
            },
        )
        if budget.get("action") == "downgrade":
            route = self._call(
                "downgrade_model",
                {
                    "from_model": route.get("model_id"),
                    "reason": "BUDGET_PRESSURE",
                    "max_relative_quality_loss": 0.15,
                },
            )
        return {"phase": "routed", "estimate": est, "budget": budget, "route": route}


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {name: _stub for name in CostOptimizerConfig().tool_allowlist}
