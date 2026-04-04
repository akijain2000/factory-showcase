"""Eval Agent — rubric, scoring pipeline, calibration, aggregation."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol

log = logging.getLogger(__name__)
ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    WAITING_TOOL = auto()
    ERROR = auto()
    DONE = auto()


_TRANS = {
    AgentState.IDLE: (AgentState.PLANNING, AgentState.ERROR),
    AgentState.PLANNING: (AgentState.EXECUTING, AgentState.ERROR, AgentState.DONE),
    AgentState.EXECUTING: (AgentState.WAITING_TOOL, AgentState.ERROR, AgentState.DONE),
    AgentState.WAITING_TOOL: (AgentState.EXECUTING, AgentState.ERROR, AgentState.DONE),
    AgentState.ERROR: (AgentState.DONE,),
    AgentState.DONE: (AgentState.IDLE,),
}


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


@dataclass
class EvalAgentConfig:
    rubric_registry_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None
    max_steps: int = 80
    max_wall_time_s: float = 180.0
    max_spend_usd: float = 10.0
    tool_timeout_s: float = 45.0
    state_path: Optional[Path] = None


class EvalAgent:
    def __init__(self, config: EvalAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.agent_state = AgentState.IDLE
        self.active_rubric_id: Optional[str] = None
        self.rubric_revision: int = 0
        self.audit: List[Dict[str, Any]] = []
        self._step = 0
        self._t0 = 0.0
        self._spend = 0.0
        self._pool = ThreadPoolExecutor(max_workers=4)

    def _goto(self, n: AgentState) -> None:
        if n not in _TRANS.get(self.agent_state, ()):
            raise RuntimeError(f"bad transition {self.agent_state!r} -> {n!r}")
        self.audit.append({"ts": time.time(), "kind": "transition", "to": n.name})
        log.info("eval_step", extra={"state": n.name})
        self.agent_state = n

    def _breakers(self) -> Optional[str]:
        if self._step >= self.config.max_steps:
            return "max_steps"
        if time.monotonic() - self._t0 > self.config.max_wall_time_s:
            return "max_wall_time"
        if self._spend >= self.config.max_spend_usd:
            return "max_spend"
        return None

    def _dispatch(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        trip = self._breakers()
        if trip:
            self._goto(AgentState.ERROR)
            return {"ok": False, "error": {"code": "CIRCUIT", "message": trip, "retryable": False}}
        self._goto(AgentState.WAITING_TOOL)
        self._step += 1
        h = self.tools.get(name)
        if not h:
            self._goto(AgentState.EXECUTING)
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name, "retryable": False}}
        fut = self._pool.submit(h, args)
        try:
            out = fut.result(timeout=self.config.tool_timeout_s)
        except FutTimeout:
            fut.cancel()
            self.audit.append({"ts": time.time(), "kind": "tool_timeout", "tool": name})
            self._goto(AgentState.EXECUTING)
            return {"ok": False, "error": {"code": "TIMEOUT", "message": name, "retryable": True}}
        if isinstance(out, dict) and out.get("cost_usd") is not None:
            self._spend += float(out["cost_usd"])
        self.audit.append({"ts": time.time(), "kind": "tool", "tool": name})
        err = out.get("error") if isinstance(out, dict) else None
        if isinstance(err, dict) and err.get("retryable") and self._step < self.config.max_steps:
            return self._dispatch(name, args)
        self._goto(AgentState.EXECUTING)
        return out

    def load_system_prompt(self) -> str:
        p = self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md"
        return p.read_text(encoding="utf-8")

    def tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        h = self.tools.get(name)
        if not h:
            return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name}}
        return h(args)

    def save_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        p.write_text(
            json.dumps(
                {
                    "agent_state": self.agent_state.name,
                    "rubric_id": self.active_rubric_id,
                    "rubric_revision": self.rubric_revision,
                    "step": self._step,
                    "spend": self._spend,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        if not p.is_file():
            return
        d = json.loads(p.read_text(encoding="utf-8"))
        self.agent_state = AgentState[d["agent_state"]]
        self.active_rubric_id = d.get("rubric_id")
        self.rubric_revision = int(d.get("rubric_revision", 0))
        self._step = int(d.get("step", 0))
        self._spend = float(d.get("spend", 0.0))

    def run(self, user_message: str, llm: LLMClient) -> str:
        self.agent_state, self._step, self._spend, self._t0 = AgentState.IDLE, 0, 0.0, time.monotonic()
        self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        plan = llm.complete(sys_p, f"List trajectory_ref JSON strings (array) to score from: {user_message[:1500]}")
        try:
            traj = json.loads(plan) if plan.strip().startswith("[") else []
        except json.JSONDecodeError:
            traj = ["default-trajectory"]
        if not traj:
            traj = ["default-trajectory"]
        spec = llm.complete(sys_p, f"Task spec for rubric (one paragraph): {user_message[:1200]}")
        self._goto(AgentState.EXECUTING)
        rub = self._dispatch("generate_rubric", {"task_spec": spec, "rubric_registry_ref": self.config.rubric_registry_ref})
        self.active_rubric_id = rub.get("rubric_id", "rubric-local")
        self.rubric_revision = int(rub.get("rubric_revision", 1))
        scores: List[Dict[str, Any]] = []
        for tref in traj[:20]:
            trip = self._breakers()
            if trip:
                self._goto(AgentState.ERROR)
                return json.dumps({"error": trip, "partial_scores": scores})
            self._dispatch("filter_by_dimension", {"rubric_id": self.active_rubric_id, "trajectory_ref": tref})
            sc = self._dispatch(
                "score_trajectory",
                {"rubric_id": self.active_rubric_id, "trajectory_ref": tref, "granularity": "both"},
            )
            scores.append({"trajectory_ref": tref, "score": sc})
        anchors = [x["trajectory_ref"] for x in scores[:3]]
        cal = self._dispatch(
            "calibrate_rubric",
            {"rubric_id": self.active_rubric_id, "anchor_trajectories": anchors, "target_metric": "human_agreement"},
        )
        agg = self._dispatch("aggregate_scores", {"scores": scores, "policy": "trimmed_mean"})
        self._goto(AgentState.DONE)
        return llm.complete(
            sys_p,
            f"Evaluation report. rubric={self.active_rubric_id} rev={self.rubric_revision}\n"
            f"calibration={json.dumps(cal)[:800]}\naggregate={json.dumps(agg)[:1200]}",
        )

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        return self.run(user_message, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {k: _stub for k in ("generate_rubric", "score_trajectory", "filter_by_dimension", "aggregate_scores", "calibrate_rubric")}
