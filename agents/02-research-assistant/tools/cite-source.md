# Tool: `cite_source`

## Purpose

Normalize and validate citation records so the final answer uses consistent metadata.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["kind", "ref"],
  "properties": {
    "kind": { "type": "string", "enum": ["web", "corpus"] },
    "ref": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string" },
        "url": { "type": "string", "format": "uri" },
        "title": { "type": "string" },
        "accessed_at": { "type": "string", "format": "date-time" },
        "doc_id": { "type": "string" },
        "chunk_id": { "type": "string" }
      }
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "citation": {
    "marker": "[1]",
    "id": "cit-1",
    "display": "Onboarding Runbook (doc-123), §3.2"
  }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CITATION_INVALID | no | `ref` missing required fields for `kind` |
| SCHEMA_MISMATCH | no | Document chunk reference inconsistent |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 10s
- Rate limit: 300 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

None.
