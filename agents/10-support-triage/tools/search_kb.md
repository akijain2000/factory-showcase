# Tool: `search_kb`

## Purpose

Retrieve knowledge-base articles and policy snippets with citation ids.

## Invocation

**MCP** tool name: `search_kb`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Search string |
| `locale` | string | no | BCP-47 tag |
| `top_k` | integer | no | Default 5 |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `hits` | array | `{ article_id, title, excerpt, url }` |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| KB_UNAVAILABLE | yes | Knowledge base temporarily unreachable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 180 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 5 (see `top_k`)
- Cursor-based: returns `next_cursor` in response
- Max results per call: 50

## Errors

- `KB_UNAVAILABLE`
