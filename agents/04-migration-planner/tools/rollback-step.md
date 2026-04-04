# Tool: `rollback_step`

## Purpose

Apply the rollback associated with a previously executed `step_id`.

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
    "reason": { "type": "string", "maxLength": 2000 },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key; rollbacks are not safe to blindly repeat."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "step_id": "s1",
  "rolled_back_at": "2026-04-04T12:05:00Z"
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| ROLLBACK_UNSUPPORTED | no | Step has no safe rollback path |
| DATA_LOSS_RISK | no | Operator confirmation required |
| STEP_NOT_APPLIED | no | Forward step never completed |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 600s
- Rate limit: 10 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: no
- Duplicate detection window: 86400s

## Side effects

Reverts the forward step when possible; may require maintenance window for some DDL.

## Errors

`ROLLBACK_UNSUPPORTED`, `DATA_LOSS_RISK` — surface to human operator.
