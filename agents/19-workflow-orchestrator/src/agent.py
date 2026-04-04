from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple

ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]

class AgentState(Enum):
    IDLE, PLANNING, EXECUTING, WAITING_TOOL, ERROR, DONE = (auto(), auto(), auto(), auto(), auto(), auto())


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
class WorkflowConfig:
    checkpoint_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None
    max_steps: int = 100
    max_wall_time_s: float = 300.0
    max_spend_usd: float = 20.0
    tool_timeout_s: float = 60.0
    state_path: Optional[Path] = None

def _topo(nodes: List[str], edges: List[Tuple[str, str]]) -> List[str]:
    pred, succ = {n: set() for n in nodes}, {n: [] for n in nodes}
    for u, v in edges:
        if u in pred and v in pred:
            pred[v].add(u)
            succ[u].append(v)
    q, out = [n for n in nodes if not pred[n]], []
    while q:
        u = q.pop(0)
        out.append(u)
        for v in succ[u]:
            pred[v].discard(u)
            if not pred[v]:
                q.append(v)
    return out if len(out) == len(nodes) else []

@dataclass
class RunContext:
    run_id: str
    dag_id: str
    revision: int
    completed: Set[str] = field(default_factory=set)
    outputs: Dict[str, Any] = field(default_factory=dict)

class WorkflowOrchestratorAgent:
    def __init__(self, config: WorkflowConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.agent_state, self.run_id = AgentState.IDLE, ""
        self.completed, self.outputs, self.audit = set(), {}, []
        self._step, self._t0, self._spend = 0, 0.0, 0.0
        self._pool = ThreadPoolExecutor(max_workers=4)

    def _goto(self, n: AgentState) -> None:
        if n not in _TRANS.get(self.agent_state, ()):
            raise RuntimeError(f"bad transition {self.agent_state!r} -> {n!r}")
        e = {"ts": time.time(), "kind": "transition", "to": n.name}
        self.audit.append(e)
        logging.getLogger(__name__).info("workflow_step", extra={"structured": json.dumps(e)})
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
        e = {"ts": time.time(), "kind": "dag_mutation", "tool": name, "step": args.get("step_id")}
        self.audit.append(e)
        logging.getLogger(__name__).info("workflow_tool", extra={"structured": json.dumps(e)})
        err = out.get("error") if isinstance(out, dict) else None
        if isinstance(err, dict) and err.get("retryable") and self._step < self.config.max_steps:
            return self._dispatch(name, args)
        self._goto(AgentState.EXECUTING)
        return out

    def load_system_prompt(self) -> str:
        return (self.config.system_prompt_path or Path(__file__).resolve().parent.parent / "system-prompt.md").read_text(encoding="utf-8")

    def tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        h = self.tools.get(name)
        return h(args) if h else {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name}}

    def plan_ready_steps(self, layers: List[List[str]], ctx: RunContext) -> List[str]:
        for layer in layers:
            p = [s for s in layer if s not in ctx.completed]
            if p:
                return p
        return []

    def save_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        d = {
            "agent_state": self.agent_state.name,
            "run_id": self.run_id,
            "completed": list(self.completed),
            "outputs": self.outputs,
            "step": self._step,
            "spend": self._spend,
        }
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        if not p.is_file():
            return
        d = json.loads(p.read_text(encoding="utf-8"))
        self.agent_state = AgentState[d["agent_state"]]
        self.run_id = d.get("run_id", "")
        self.completed, self.outputs = set(d.get("completed", [])), dict(d.get("outputs", {}))
        self._step, self._spend = int(d.get("step", 0)), float(d.get("spend", 0.0))

    def run(self, user_message: str, llm: LLMClient) -> str:
        self.agent_state, self._step, self._spend, self._t0 = AgentState.IDLE, 0, 0.0, time.monotonic()
        self.completed.clear()
        self.outputs.clear()
        self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        spec = llm.complete(sys_p, f"JSON {{nodes,edges,branches}} edges=[pairs] goal: {user_message[:1500]}")
        try:
            dag = json.loads(spec) if "{" in spec else {}
        except json.JSONDecodeError:
            dag = {}
        nodes, edges = dag.get("nodes") or ["start", "end"], [tuple(e) for e in (dag.get("edges") or [("start", "end")])]
        branches: Dict[str, str] = dag.get("branches") or {}
        order = _topo(nodes, edges)
        if not order:
            self._goto(AgentState.ERROR)
            return json.dumps({"error": "cycle_or_invalid_dag"})
        self.run_id = f"run-{int(time.time() * 1000)}"
        self._goto(AgentState.EXECUTING)
        self._dispatch("define_dag", {"run_id": self.run_id, "nodes": nodes, "edges": edges, "revision": 1})
        for sid in order:
            trip = self._breakers()
            if trip:
                self._goto(AgentState.ERROR)
                return json.dumps({"error": trip, "last_step": sid})
            if (expr := branches.get(sid)):
                ev = self._dispatch("evaluate_condition", {"run_id": self.run_id, "expression_ref": expr, "facts": dict(self.outputs)})
                if not ev.get("continue", True):
                    self.audit.append({"kind": "branch_skip", "step": sid})
                    continue
            ex = self._dispatch("execute_step", {"run_id": self.run_id, "step_id": sid, "inputs": self.outputs, "user_goal": user_message[:500]})
            self.completed.add(sid)
            if ex.get("output_ref"):
                self.outputs[sid] = ex["output_ref"]
            self._dispatch("checkpoint_state", {"run_id": self.run_id, "cursor": sid, "checkpoint_ref": self.config.checkpoint_ref})
        self._goto(AgentState.DONE)
        pct = int(100 * len(self.completed) / max(len(nodes), 1))
        return llm.complete(sys_p, f"Summary run_id={self.run_id} pct={pct} keys={list(self.outputs)}")

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        return self.run(user_message, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    stub = lambda _: {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}
    return {k: stub for k in ("define_dag", "execute_step", "checkpoint_state", "resume_from_checkpoint", "evaluate_condition")}
