# Tool: `aggregate_stream`

## Purpose

Define or query a **stateful aggregation** over an event stream: windows, sessions, or keyed folds with late-data handling.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["topic", "window", "aggregate_id"],
  "properties": {
    "topic": { "type": "string", "maxLength": 256 },
    "aggregate_id": { "type": "string", "maxLength": 128 },
    "partition_key": { "type": "string", "maxLength": 512 },
    "window": {
      "type": "object",
      "required": ["type"],
      "additionalProperties": false,
      "properties": {
        "type": {
          "type": "string",
          "enum": ["tumbling", "sliding", "session"]
        },
        "size_ms": { "type": "integer", "minimum": 1, "maximum": 86400000 },
        "slide_ms": { "type": "integer", "minimum": 1, "maximum": 86400000 },
        "session_gap_ms": { "type": "integer", "minimum": 1, "maximum": 3600000 },
        "allowed_lateness_ms": { "type": "integer", "minimum": 0, "maximum": 3600000, "default": 0 }
      }
    },
    "fold": {
      "type": "string",
      "enum": ["count", "sum", "max", "custom_ref"],
      "default": "count"
    },
    "custom_fold_ref": { "type": "string", "maxLength": 256 },
    "emit_mode": {
      "type": "string",
      "enum": ["on_window_close", "continuous"],
      "default": "on_window_close"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "aggregate_id": "agg_tokens_per_session",
  "state_handle": "stm_4nQs81",
  "last_emitted_at": "2026-04-04T12:00:05Z",
  "notes": ["Late events within 2s lateness merged."]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| AGGREGATE_CONFLICT | no | Incompatible definition for existing `aggregate_id` |
| TOPIC_NOT_FOUND | no | Unknown `topic` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `aggregate_id` (required; repeated calls with identical window/fold definition are idempotent)
- Safe to retry: yes
- Duplicate detection window: 600s

## Side effects

Allocates or updates durable **state store** handles; may create internal changelog topics. Continuous mode increases write amplification—monitor with `inspect_backpressure`.
