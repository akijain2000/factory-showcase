# Tool: `store_memory`

## Purpose

Persist durable **research context** for the session or user (hypotheses, source lists, follow-ups).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["key", "content"],
  "properties": {
    "key": {
      "type": "string",
      "pattern": "^[a-z0-9._-]{1,64}$",
      "description": "Stable key, e.g. session.open_questions"
    },
    "content": { "type": "string", "maxLength": 32000 },
    "ttl_seconds": { "type": "integer", "minimum": 60, "maximum": 2592000 },
    "pii": { "type": "boolean", "default": false, "description": "Must be false unless policy allows" },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key for safe retries."
    }
  }
}
```

## Return shape

```json
{ "ok": true, "stored": true, "key": "session.open_questions", "version": 3 }
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| POLICY_PII_DENY | no | `pii: true` not allowed by policy |
| QUOTA_EXCEEDED | no | Memory quota or size limit hit |
| STORAGE_UNAVAILABLE | yes | Backend transient failure |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Side effects

Writes to memory backend.

## Constraints

Implementations **must reject** `pii: true` unless enterprise policy enables redacted storage.
