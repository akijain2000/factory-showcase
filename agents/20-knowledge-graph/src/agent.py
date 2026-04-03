"""
Knowledge Graph Agent — ingest, query, and path reasoning loop (stub).

Coordinates extraction, relationship mapping, bounded traversals, subgraph
retrieval, and structured explanations over paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class KnowledgeGraphConfig:
    graph_store_ref: Optional[str] = None
    embed_index_ref: Optional[str] = None
    system_prompt_path: Optional[Path] = None


class KnowledgeGraphAgent:
    def __init__(self, config: KnowledgeGraphConfig, tools: Dict[str, ToolHandler]) -> None:
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

    def ingest_document(self, document_ref: str, text: str) -> Dict[str, Any]:
        entities = self.tool(
            "extract_entities",
            {"document_ref": document_ref, "text": text, "linking_mode": "embeddings"},
        )
        ids = [e["id"] for e in entities.get("entities", [])]
        rels = self.tool(
            "map_relationships",
            {"document_ref": document_ref, "entity_ids": ids, "candidates": []},
        )
        return {"entities": entities, "relationships": rels}

    def answer_with_graph(
        self, question: str, seeds: List[str], max_hops: int
    ) -> Dict[str, Any]:
        walk = self.tool(
            "traverse_graph",
            {
                "seeds": seeds,
                "max_hops": max_hops,
                "direction": "out",
                "allowed_predicates": ["PART_OF", "OWNS_SERVICE", "DEPENDS_ON"],
            },
        )
        sub = self.tool(
            "query_subgraph",
            {
                "pattern": "typed_neighborhood",
                "bindings": {"center": seeds[0] if seeds else ""},
                "limit": 120,
            },
        )
        reason = self.tool(
            "reason_over_path",
            {
                "question": question,
                "context": {"edges": walk.get("edges", [])},
                "answer_style": "concise",
            },
        )
        return {"traverse": walk, "subgraph": sub, "reason": reason}

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Implement retrieval + tool loop with your runtime.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "extract_entities": _stub,
        "map_relationships": _stub,
        "traverse_graph": _stub,
        "query_subgraph": _stub,
        "reason_over_path": _stub,
    }
