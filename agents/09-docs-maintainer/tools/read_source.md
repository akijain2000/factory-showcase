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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PATH_OUTSIDE_REPO | no | Path violates repository safety boundary |
| NOT_FOUND | no | File or range not found |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 300 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `PATH_OUTSIDE_REPO` — violates safety **constraints**
- `NOT_FOUND`
