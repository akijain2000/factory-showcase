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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| WINDOW_TOO_LARGE | no | Narrow `start`/`end` range |
| RATE_LIMITED | yes | Log provider quota |
| QUERY_SYNTAX_ERROR | no | Invalid `query` fragment |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 500
- Cursor-based: returns `next_cursor` in response
- Max results per call: 5000

## Errors

- `WINDOW_TOO_LARGE` — narrow range
- `RATE_LIMITED`
