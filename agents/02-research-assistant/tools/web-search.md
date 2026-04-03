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

## Side effects

Outbound network call; may incur cost. Rate-limit per session.

## Errors

`RATE_LIMIT`, `PROVIDER_ERROR` (retryable with backoff), `BAD_QUERY`.
