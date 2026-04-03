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
    }
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

## Side effects

- Updates **session/tenant quota** in the executor control plane.
- May cause **backpressure** on queued `fan_out` requests until capacity frees.
- Emits an **audit event** with `reason` when the deployment requires justification for limit changes.
