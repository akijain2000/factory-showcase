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

## Side effects

Allocates or updates durable **state store** handles; may create internal changelog topics. Continuous mode increases write amplification—monitor with `inspect_backpressure`.
