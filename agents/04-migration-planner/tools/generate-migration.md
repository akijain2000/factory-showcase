# Tool: `generate_migration`

## Purpose

Generate migration artifacts: ordered forward operations each with matching rollback and a stable `step_id`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["intent", "dialect"],
  "properties": {
    "intent": { "type": "string", "description": "Natural language + constraints" },
    "dialect": { "type": "string", "enum": ["postgres", "mysql", "sqlite", "terraform", "kubernetes"] },
    "safety": {
      "type": "string",
      "enum": ["online", "locking_ok", "maintenance_window"],
      "default": "online"
    },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key for artifact writes."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "migration_id": "mgr-20260404-01",
  "steps": [
    {
      "step_id": "s1",
      "forward": "ALTER TABLE ...",
      "rollback": "ALTER TABLE ...",
      "depends_on": []
    }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| INTENT_AMBIGUOUS | no | Clarify constraints before generation |
| DIALECT_UNSUPPORTED | no | `dialect` not enabled |
| GENERATION_FAILED | yes | LLM or template engine transient error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 20 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 300s

## Side effects

Writes migration files or records in migration registry (implementation-defined).
