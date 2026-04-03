"""
Skeleton MCP client for docs-maintainer.
List tools from server, then dispatch model-selected invokes.
"""

from __future__ import annotations

from typing import Any, Protocol


class MCPTransport(Protocol):
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


def read_source(transport: MCPTransport, path: str, start_line: int | None = None, end_line: int | None = None) -> dict[str, Any]:
    return transport.call_tool(
        "read_source",
        {"path": path, "start_line": start_line, "end_line": end_line},
    )


def diff_changes(transport: MCPTransport, base: str, head: str, pathspecs: list[str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"base": base, "head": head}
    if pathspecs:
        payload["pathspecs"] = pathspecs
    return transport.call_tool("diff_changes", payload)


def update_doc(transport: MCPTransport, path: str, patch: str, rationale: str) -> dict[str, Any]:
    return transport.call_tool("update_doc", {"path": path, "patch": patch, "rationale": rationale})


def check_links(transport: MCPTransport, paths: list[str], check_external: bool = False) -> dict[str, Any]:
    return transport.call_tool(
        "check_links",
        {"paths": paths, "check_external": check_external},
    )


def search_codebase(transport: MCPTransport, query: str, path_prefix: str | None = None, max_results: int = 50) -> dict[str, Any]:
    payload: dict[str, Any] = {"query": query, "max_results": max_results}
    if path_prefix:
        payload["path_prefix"] = path_prefix
    return transport.call_tool("search_codebase", payload)


def sync_docs_from_diff(transport: MCPTransport, base: str, head: str) -> str:
    """Skeleton: diff → search → read → patch → link check. Implement LLM loop."""
    raise NotImplementedError
