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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| BROKER_REJECT | yes | Event bus refused publish (capacity, ACL, schema) |
| SCHEMA_MISMATCH | no | Payload incompatible with `schema_version` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 2000 calls per minute per `producer_id`
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `correlation_id` (optional field in arguments; pairs with `topic` + `partition_key` for dedupe)
- Safe to retry: yes when `delivery` supports at-least-once deduplication
- Duplicate detection window: 120s

## Side effects

Writes to `EVENT_BUS_ENDPOINT` (or internal broker). May trigger interceptor chain execution synchronously or asynchronously depending on deployment. Emits metrics: `emit_latency_ms`, `payload_bytes`. **No** direct call to `MODEL_API_ENDPOINT` from this tool.
