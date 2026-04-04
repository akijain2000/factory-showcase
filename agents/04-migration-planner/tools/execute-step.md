# Tool: `execute_step`

## Purpose

Execute exactly one forward migration step.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["migration_id", "step_id"],
  "properties": {
    "migration_id": { "type": "string" },
    "step_id": { "type": "string" },
    "idempotency_key": { "type": "string", "format": "uuid" }
  }
}
```

## Preconditions

Runtime MUST verify `MIGRATION_ALLOW_EXECUTE=true` and prior `dry_run` success for this `step_id` unless policy overrides (dev).

## Return shape

```json
{
  "ok": true,
  "step_id": "s1",
  "applied_at": "2026-04-04T12:00:00Z",
  "verification": { "row_count_check": "passed" }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| GATE_FAILED | no | `MIGRATION_ALLOW_EXECUTE` or dry-run gate failed |
| EXECUTION_ERROR | yes | DB error after rollback; safe retry depends on step |
| LOCK_NOT_AVAILABLE | yes | Could not acquire migration lock |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 3600s
- Rate limit: 20 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

Mutates database or infrastructure.

## Errors

`GATE_FAILED`, `EXECUTION_ERROR` (may be retryable if transaction rolled back).
