# Tool: `inspect_backpressure`

## Purpose

Read **lag**, **queue depth**, and **flow control** signals for topics and consumer groups to guide scaling, shedding, or cancellation.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["consumer_group"],
  "properties": {
    "consumer_group": { "type": "string", "maxLength": 128 },
    "topics": {
      "type": "array",
      "items": { "type": "string", "maxLength": 256 },
      "maxItems": 32
    },
    "sample_limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 5 },
    "include_partition_breakdown": { "type": "boolean", "default": true }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "lag_max_seconds": 42.7,
  "depth_estimate": 185000,
  "flow_control": {
    "publisher_throttled": false,
    "consumer_paused_partitions": [1]
  },
  "partitions": [
    { "id": 0, "lag_seconds": 12.1, "pending": 42000 },
    { "id": 1, "lag_seconds": 42.7, "pending": 98000 }
  ],
  "redacted_samples": [
    {
      "topic": "llm.tokens.v1",
      "preview": "{... redacted ...}",
      "approx_bytes": 2048
    }
  ]
}
```

## Side effects

Read-only against `BACKPRESSURE_METRICS_REF` / broker APIs. May increment a **cached read** counter for rate limiting telemetry. Does not mutate pipeline topology.
