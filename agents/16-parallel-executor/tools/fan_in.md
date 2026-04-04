# Tool: `fan_in`

## Purpose

**Merge** completed shard outputs into a single structured response using a declared strategy, preserving deterministic ordering and attaching merge provenance.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["correlation_id", "merge_strategy", "shard_results"],
  "properties": {
    "correlation_id": { "type": "string", "minLength": 8, "maxLength": 256 },
    "merge_strategy": {
      "type": "string",
      "enum": ["concat", "reduce_by_key", "vote", "custom_ref"]
    },
    "shard_results": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["shard_id", "status"],
        "properties": {
          "shard_id": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["succeeded", "failed", "timeout", "cancelled", "skipped"]
          },
          "sort_key": { "type": "string" },
          "result": { "type": "object" },
          "error": {
            "type": "object",
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" }
            }
          }
        }
      }
    },
    "custom_merge_ref": {
      "type": "string",
      "description": "Registry key for a registered reducer when strategy is custom_ref."
    },
    "fail_if_any_failed": { "type": "boolean", "default": false },
    "merge_idempotency_key": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "status": "complete_with_errors",
  "merged": {
    "items": [],
    "metrics": { "succeeded": 7, "failed": 1, "skipped": 0 }
  },
  "ordering": "sort_key_lexical",
  "provenance": { "merge_strategy": "concat", "correlation_id": "corr_01HXYZ" }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| MERGE_FAILED | no | Reducer or merge strategy produced an invalid result |
| STRATEGY_UNKNOWN | no | `merge_strategy` or `custom_merge_ref` not registered |
| INCOMPLETE_SHARDS | no | Required shard results missing for merge |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 300 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `merge_idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

- Writes a **merge span** linked to `correlation_id` in the trace store.
- May emit **metrics** (histogram of shard latencies) to the monitoring backend.
- When `fail_if_any_failed` is true, returns non-success without mutating durable user state beyond audit logs.
