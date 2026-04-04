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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| QUERY_REJECTED | no | Pattern blocked by host safety policy |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 90 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 50
- Cursor-based: returns `next_cursor` in response
- Max results per call: 500

## Errors

- `QUERY_REJECTED` — unsafe pattern per host **constraints**
