"""
Research Assistant — ReAct + RAG skeleton.

Wires tool names: web_search, retrieve_document, store_memory, cite_source.
Replace LLM and backends with your stack; enforce memory redaction in store_memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class ResearchAgentConfig:
    memory_store_uri: str
    doc_index_id: str
    max_web_results: int = 5
    system_prompt_path: Optional[Path] = None


@dataclass
class ResearchState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    step: int = 0
    citation_counter: int = 0


class ResearchAssistantAgent:
    def __init__(self, config: ResearchAgentConfig, tools: Dict[str, ToolHandler]) -> None:
        self.config = config
        self.tools = tools
        self.state = ResearchState()

    def load_system_prompt(self) -> str:
        path = self.config.system_prompt_path or (
            Path(__file__).resolve().parent.parent / "system-prompt.md"
        )
        return path.read_text(encoding="utf-8")

    def run_turn(self, user_message: str, llm_client: Any) -> str:
        raise NotImplementedError("Implement ReAct loop + RAG routing.")


def default_tool_registry() -> Dict[str, ToolHandler]:
    def _stub(_: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "error": {"code": "NOT_IMPLEMENTED", "message": "stub"}}

    return {
        "web_search": _stub,
        "retrieve_document": _stub,
        "store_memory": _stub,
        "cite_source": _stub,
    }
