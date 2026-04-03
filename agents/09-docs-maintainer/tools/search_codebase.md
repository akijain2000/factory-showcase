# MCP Tool: `search_codebase`

## Purpose

Search code for symbols, strings, or patterns to align docs with implementation.

## Invocation

**Function calling** / **MCP**: `search_codebase`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Pattern or symbol |
| `path_prefix` | string | no | Subtree |
| `max_results` | integer | no | Default 50 |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `matches` | array | `{ path, line, snippet }` |

## Errors

- `QUERY_REJECTED` — unsafe pattern per host **constraints**
