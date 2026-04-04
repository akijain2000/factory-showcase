# Tool: `web_search`

## Purpose

Run a web search query and return ranked results with titles, URLs, and snippets.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["query"],
  "properties": {
    "query": { "type": "string", "minLength": 1, "maxLength": 500 },
    "max_results": { "type": "integer", "minimum": 1, "maximum": 20, "default": 5 },
    "language": { "type": "string", "description": "BCP 47 tag, e.g. en" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "results": [
    {
      "rank": 1,
      "title": "...",
      "url": "https://example.com",
      "snippet": "...",
      "retrieved_at": "2026-04-04T00:00:00Z"
    }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RATE_LIMIT | yes | Provider or session quota exceeded |
| PROVIDER_ERROR | yes | Upstream search API failure |
| BAD_QUERY | no | Empty, too long, or blocked query |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 5
- Cursor-based: returns `next_cursor` in response
- Max results per call: 20

## Side effects

Outbound network call; may incur cost. Rate-limit per session.

## Errors

`RATE_LIMIT`, `PROVIDER_ERROR` (retryable with backoff), `BAD_QUERY`.
