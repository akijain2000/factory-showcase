# Tool: `retrieve_document`

## Purpose

Retrieve relevant chunks from the configured document index (vector + metadata filter).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["query"],
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "top_k": { "type": "integer", "minimum": 1, "maximum": 32, "default": 8 },
    "filters": {
      "type": "object",
      "additionalProperties": { "type": "string" },
      "description": "Metadata filters, e.g. {\"project_id\": \"payments\"}"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "chunks": [
    {
      "doc_id": "doc-123",
      "chunk_id": "doc-123#4",
      "text": "...",
      "score": 0.82,
      "metadata": { "title": "Onboarding Runbook", "section": "3.2" }
    }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| INDEX_UNAVAILABLE | yes | Vector or metadata index unreachable |
| QUERY_TIMEOUT | yes | Retrieval exceeded deadline |
| FILTER_REJECTED | no | Invalid or unsupported metadata filter |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 90 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 8
- Cursor-based: returns `next_cursor` in response
- Max results per call: 32

## Side effects

Read-only against index.

## Auth

Service credentials via environment; never passed in prompt.
