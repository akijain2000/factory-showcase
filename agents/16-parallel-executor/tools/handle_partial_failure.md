# Tool: `handle_partial_failure`

## Purpose

Apply a **declared recovery policy** when one or more shards fail, time out, or are cancelled—coordinating retries, compensating actions, or controlled abort without corrupting merged state.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["correlation_id", "policy", "failed_shard_ids"],
  "properties": {
    "correlation_id": { "type": "string", "minLength": 8, "maxLength": 256 },
    "policy": {
      "type": "string",
      "enum": ["continue_with_partial", "retry_failed", "abort_merge", "compensate"]
    },
    "failed_shard_ids": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "retry": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "max_attempts": { "type": "integer", "minimum": 1, "maximum": 5, "default": 2 },
        "backoff_ms": { "type": "integer", "minimum": 0, "maximum": 600000, "default": 500 },
        "jitter": { "type": "boolean", "default": true }
      }
    },
    "compensation_plan_ref": {
      "type": "string",
      "description": "Reference to registered compensator when policy is compensate."
    }
  }
}
```

## Return shape

```json
{
  "decision": "retry_failed",
  "correlation_id": "corr_01HXYZ",
  "actions": [
    { "shard_id": "s4", "action": "requeue", "attempt": 2, "handle": "job_a12c" }
  ],
  "blocked_merge": false,
  "notes": []
}
```

## Side effects

- May **requeue** shards, creating new job handles and trace child spans.
- For `abort_merge`, may mark the correlation as **terminal** in the workflow state machine.
- For `compensate`, may invoke registered side-effect handlers—must be audited per deployment policy.
