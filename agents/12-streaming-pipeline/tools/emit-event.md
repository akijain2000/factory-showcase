# Tool: `emit_event`

## Purpose

Publish a single **canonical** event to the unified bus with schema version, partition key, and trace correlation fields.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["topic", "payload", "schema_version"],
  "properties": {
    "topic": { "type": "string", "maxLength": 256 },
    "partition_key": { "type": "string", "maxLength": 512 },
    "schema_version": { "type": "string", "maxLength": 32 },
    "payload": { "type": "object", "additionalProperties": true },
    "causation_id": { "type": "string", "maxLength": 128 },
    "correlation_id": { "type": "string", "maxLength": 128 },
    "producer_id": { "type": "string", "maxLength": 128 },
    "delivery": {
      "type": "string",
      "enum": ["at_least_once", "exactly_once_best_effort"],
      "default": "at_least_once"
    },
    "ttl_ms": { "type": "integer", "minimum": 0, "maximum": 86400000 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "event_id": "evt_9K2mLq",
  "topic": "llm.tokens.v1",
  "partition": 3,
  "offset": 91028374655
}
```

## Side effects

Writes to `EVENT_BUS_ENDPOINT` (or internal broker). May trigger interceptor chain execution synchronously or asynchronously depending on deployment. Emits metrics: `emit_latency_ms`, `payload_bytes`. **No** direct call to `MODEL_API_ENDPOINT` from this tool.
