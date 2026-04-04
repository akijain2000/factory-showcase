# Tool: `set_concurrency_limit`

## Purpose

Set or lower the **maximum in-flight** child executions for the current session or tenant. Used to enforce fairness, protect downstream services, and comply with rate limits.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["limit"],
  "properties": {
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 256,
      "description": "Hard cap for concurrent shard executions."
    },
    "scope": {
      "type": "string",
      "enum": ["session", "tenant", "global_hint"],
      "default": "session"
    },
    "reason": {
      "type": "string",
      "maxLength": 500,
      "description": "Human-readable rationale for audit logs."
    },
    "effective_after_ms": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Delay before applying decrease to running work (grace window)."
    },
    "limit_change_token": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "previous_limit": 32,
  "new_limit": 16,
  "scope": "session",
  "applied_at_ms": 1712230400123,
  "policy_warnings": []
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| LIMIT_OUT_OF_BOUNDS | no | `limit` below deployment minimum or above hard cap |
| SCOPE_DENIED | no | Caller cannot change `scope` (e.g. `global_hint` restricted) |
| QUOTA_SERVICE_ERROR | yes | Control plane unavailable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `limit_change_token` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 300s

## Side effects

- Updates **session/tenant quota** in the executor control plane.
- May cause **backpressure** on queued `fan_out` requests until capacity frees.
- Emits an **audit event** with `reason` when the deployment requires justification for limit changes.
