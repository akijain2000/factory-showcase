# Tool: `query_logs`

## Purpose

Search structured logs within a bounded time window.

## Invocation

**MCP** tool name: `query_logs`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `service` | string | yes | Service filter |
| `start` | string | yes | ISO-8601 start |
| `end` | string | yes | ISO-8601 end |
| `query` | string | no | Query language fragment |
| `limit` | integer | no | Max rows (default 500, cap 5000) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `rows` | array | Log entries |
| `truncated` | boolean | Whether more rows exist |

## Errors

- `WINDOW_TOO_LARGE` — narrow range
- `RATE_LIMITED`
