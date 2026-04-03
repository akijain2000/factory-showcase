# MCP Tool: `read_source`

## Purpose

Read repository files with optional line range for grounding doc updates.

## Invocation

Registered on MCP server as `read_source`; models **invoke** via **function calling** bridge.

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Repo-relative path |
| `start_line` | integer | no | 1-based inclusive |
| `end_line` | integer | no | 1-based inclusive |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | File slice or full file |
| `sha256` | string | Content hash for cache busting |

## Errors

- `PATH_OUTSIDE_REPO` — violates safety **constraints**
- `NOT_FOUND`
