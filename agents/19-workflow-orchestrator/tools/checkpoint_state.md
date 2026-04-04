# Tool: `checkpoint_state`

## Purpose

Persist a **durable snapshot** of workflow progress: completed steps, branch decisions, cursor position, and artifact references for resume.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["run_id", "cursor", "state"],
  "properties": {
    "run_id": { "type": "string", "maxLength": 256 },
    "cursor": {
      "type": "object",
      "required": ["layer_index", "pending_step_ids"],
      "properties": {
        "layer_index": { "type": "integer", "minimum": 0 },
        "pending_step_ids": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "state": {
      "type": "object",
      "required": ["completed", "outputs"],
      "properties": {
        "completed": {
          "type": "array",
          "items": { "type": "string" }
        },
        "outputs": { "type": "object" },
        "branch_decisions": { "type": "object" },
        "notes": { "type": "string", "maxLength": 4000 }
      }
    },
    "ttl_hours": { "type": "integer", "minimum": 1, "maximum": 720, "default": 168 },
    "checkpoint_idempotency_key": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "checkpoint_id": "cp_9f2a",
  "run_id": "run_884",
  "stored_at_ms": 1712231000000,
  "size_bytes": 18233
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| STORAGE_QUOTA | no | Checkpoint store quota exceeded |
| RUN_NOT_FOUND | no | Unknown `run_id` |
| SERIALIZATION_ERROR | no | `state` could not be encoded |
| ENCRYPTION_ERROR | yes | At-rest encryption transient failure |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 100 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `checkpoint_idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

- Writes to **checkpoint store**; may compress and encrypt at rest.
- Increments **checkpoint sequence** for the run (used in resume conflict detection).
