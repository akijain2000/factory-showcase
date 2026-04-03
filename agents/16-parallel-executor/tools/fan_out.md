# Tool: `fan_out`

## Purpose

Schedule **multiple independent child executions** (tool calls, jobs, or HTTP tasks) under a shared `correlation_id`, respecting the active concurrency limit and shard priorities.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["correlation_id", "shards"],
  "properties": {
    "correlation_id": {
      "type": "string",
      "minLength": 8,
      "maxLength": 256,
      "description": "End-to-end idempotency and trace root identifier."
    },
    "shards": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "payload"],
        "properties": {
          "id": { "type": "string", "maxLength": 128 },
          "payload": {
            "type": "object",
            "description": "Opaque to orchestrator; validated by downstream tool adapter."
          },
          "priority": { "type": "integer", "minimum": 0, "maximum": 100, "default": 50 },
          "timeout_ms": { "type": "integer", "minimum": 100, "maximum": 600000 },
          "target_tool": { "type": "string", "maxLength": 128 }
        }
      }
    },
    "queue_overflow": {
      "type": "string",
      "enum": ["block", "reject", "degrade_to_serial"],
      "default": "block"
    }
  }
}
```

## Return shape

```json
{
  "accepted": true,
  "correlation_id": "corr_01HXYZ",
  "scheduled": [
    { "shard_id": "s1", "handle": "job_9f3a", "state": "queued" }
  ],
  "deferred": [],
  "concurrency_limit": 16,
  "policy_warnings": []
}
```

## Side effects

- Enqueues work on the executor queue; may create **trace root** span records.
- May persist **shard lease** metadata for timeout and cancellation.
- Does **not** perform merges; callers must await completion signals or poll handles out-of-band per runtime.
