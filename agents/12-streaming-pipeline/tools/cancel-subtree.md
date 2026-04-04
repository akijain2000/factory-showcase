# Tool: `cancel_subtree`

## Purpose

Request **hierarchical cancellation** starting at `scope_id`, optionally draining in-flight work within `grace_ms`. Propagates to child scopes according to `propagate_to`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["scope_id"],
  "properties": {
    "scope_id": { "type": "string", "maxLength": 256 },
    "reason_code": { "type": "string", "maxLength": 64 },
    "grace_ms": { "type": "integer", "minimum": 0, "maximum": 600000, "default": 2000 },
    "propagate_to": {
      "type": "string",
      "enum": ["none", "children", "descendants"],
      "default": "descendants"
    },
    "force": { "type": "boolean", "default": false },
    "idempotency_key": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "scope_id": "job/4821/step-3",
  "status": "draining",
  "child_scopes": ["job/4821/step-3/window-a", "job/4821/step-3/window-b"],
  "deadline_epoch_ms": 1712234567890
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| SCOPE_NOT_FOUND | no | Unknown `scope_id` |
| CANCEL_IN_PROGRESS | yes | Concurrent cancel already draining |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 200 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Side effects

Signals cooperative cancel tokens; may **nack** or redirect pending events per policy. When `force: true`, hard-stops workers after grace—use only with break-glass role. Writes cancellation audit with `reason_code` and actor. Idempotent for identical `idempotency_key`.
