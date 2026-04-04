"""Knowledge graph agent — extract, relate, traverse, subgraph, path reasoning."""

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
class KnowledgeGraphConfig:
    graph_store_ref: Optional[str] = None
    embed_index_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None
    max_steps: int = 64
    max_wall_time_s: float = 120.0
    max_spend_usd: float = 8.0
    tool_timeout_s: float = 40.0
    state_path: Optional[Path] = None
    max_hops: int = 4


class KnowledgeGraphAgent:
    def __init__(self, config: KnowledgeGraphConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config, self.tools = config, tools
        self.agent_state, self.audit = AgentState.IDLE, []
        self._step, self._t0, self._spend = 0, 0.0, 0.0
        self._pool = ThreadPoolExecutor(max_workers=4)

    def _goto(self, n: AgentState) -> None:
        if n not in _TRANS.get(self.agent_state, ()):
            raise RuntimeError(f"bad transition {self.agent_state!r} -> {n!r}")
        self.audit.append({"ts": time.time(), "kind": "transition", "to": n.name})
        log.info("kg_agent", extra={"state": n.name})
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
        self.audit.append({"ts": time.time(), "kind": "graph_mutation", "tool": name})
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
        return h(args) if h else {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": name}}

    def save_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        p.write_text(json.dumps({"agent_state": self.agent_state.name, "step": self._step, "spend": self._spend}, indent=2), encoding="utf-8")

    def load_state(self, path: Optional[Path] = None) -> None:
        p = path or self.config.state_path or Path(__file__).resolve().parent / "agent_state.json"
        if p.is_file():
            d = json.loads(p.read_text(encoding="utf-8"))
            self.agent_state = AgentState[d["agent_state"]]
            self._step, self._spend = int(d.get("step", 0)), float(d.get("spend", 0.0))

    def ingest_document(self, document_ref: str, text: str) -> Dict[str, Any]:
        ent = self.tool("extract_entities", {"document_ref": document_ref, "text": text, "linking_mode": "embeddings", "index_ref": self.config.embed_index_ref})
        ids = [e["id"] for e in ent.get("entities", []) if isinstance(e, dict) and "id" in e]
        rel = self.tool("map_relationships", {"document_ref": document_ref, "entity_ids": ids, "candidates": []})
        return {"entities": ent, "relationships": rel}

    def answer_with_graph(self, question: str, seeds: List[str], max_hops: int) -> Dict[str, Any]:
        walk = self.tool(
            "traverse_graph",
            {"seeds": seeds, "max_hops": max_hops, "direction": "out", "allowed_predicates": ["PART_OF", "OWNS_SERVICE", "DEPENDS_ON"], "store_ref": self.config.graph_store_ref},
        )
        sub = self.tool("query_subgraph", {"pattern": "typed_neighborhood", "bindings": {"center": seeds[0] if seeds else ""}, "limit": 120})
        reason = self.tool("reason_over_path", {"question": question, "context": {"edges": walk.get("edges", [])}, "answer_style": "concise"})
        return {"traverse": walk, "subgraph": sub, "reason": reason}

    def run(self, user_message: str, llm: LLMClient) -> str:
        self.agent_state, self._step, self._spend, self._t0 = AgentState.IDLE, 0, 0.0, time.monotonic()
        self._goto(AgentState.PLANNING)
        sys_p = self.load_system_prompt()
        meta = llm.complete(sys_p, f"JSON {{document_ref,seeds,question}} from: {user_message[:2000]}")
        try:
            m = json.loads(meta) if "{" in meta else {}
        except json.JSONDecodeError:
            m = {}
        doc_ref, seeds = m.get("document_ref", "doc-1"), m.get("seeds") or ["seed:0"]
        q = m.get("question") or user_message[:500]
        self._goto(AgentState.EXECUTING)
        ent = self._dispatch("extract_entities", {"document_ref": doc_ref, "text": user_message, "linking_mode": "embeddings", "index_ref": self.config.embed_index_ref})
        ids = [e["id"] for e in ent.get("entities", []) if isinstance(e, dict) and "id" in e]
        self._dispatch("map_relationships", {"document_ref": doc_ref, "entity_ids": ids or seeds, "candidates": []})
        h = self.config.max_hops
        walk = self._dispatch("traverse_graph", {"seeds": seeds, "max_hops": h, "direction": "out", "allowed_predicates": ["PART_OF", "OWNS_SERVICE", "DEPENDS_ON"], "store_ref": self.config.graph_store_ref})
        if not walk.get("ok", True) and walk.get("error", {}).get("retryable"):
            walk = self._dispatch("traverse_graph", {"seeds": seeds, "max_hops": h, "direction": "out", "allowed_predicates": ["PART_OF", "OWNS_SERVICE", "DEPENDS_ON"], "store_ref": self.config.graph_store_ref})
        sub = self._dispatch("query_subgraph", {"pattern": "typed_neighborhood", "bindings": {"center": seeds[0]}, "limit": 120})
        reason = self._dispatch("reason_over_path", {"question": q, "context": {"edges": walk.get("edges", []), "subgraph": sub}, "answer_style": "concise"})
        self._goto(AgentState.DONE)
        return llm.complete(sys_p, f"Final KG answer for {q!r} using:\n{json.dumps(reason)[:4000]}")

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        return self.run(user_message, llm_client)


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub", "retryable": False}}

    return {k: _stub for k in ("extract_entities", "map_relationships", "traverse_graph", "query_subgraph", "reason_over_path")}
