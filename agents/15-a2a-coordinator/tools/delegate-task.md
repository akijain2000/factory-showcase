# Tool: `delegate_task`

## Purpose

Send **subtasks** to peer agents under an agreed `protocol_id`, returning **task handles** for tracking.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["protocol_id", "subtasks"],
  "properties": {
    "protocol_id": { "type": "string", "maxLength": 128 },
    "subtasks": {
      "type": "array",
      "maxItems": 50,
      "items": {
        "type": "object",
        "required": ["agent_id", "objective", "inputs_ref"],
        "additionalProperties": false,
        "properties": {
          "agent_id": { "type": "string", "maxLength": 256 },
          "objective": { "type": "string", "maxLength": 8000 },
          "inputs_ref": { "type": "string", "maxLength": 512 },
          "definition_of_done": {
            "type": "array",
            "items": { "type": "string", "maxLength": 2000 },
            "maxItems": 16
          },
          "timeout_ms": { "type": "integer", "minimum": 100, "maximum": 3600000 },
          "priority": {
            "type": "string",
            "enum": ["low", "normal", "high"],
            "default": "normal"
          }
        }
      }
    },
    "deadline_ms": { "type": "integer", "minimum": 100, "maximum": 7200000 },
    "idempotency_key": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "task_handles": [
    {
      "handle": "tsk_9pQm01",
      "agent_id": "svc/code-analyzer@v3",
      "state": "queued"
    }
  ],
  "bus_message_ids": ["msg_3nQs81"]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| BUS_UNAVAILABLE | yes | Message bus or queue temporarily unavailable |
| POLICY_DENIED | no | `POLICY_GATE_REF` rejected payload classification |
| PEER_REJECTED | no | Target agent refused subtask (capacity, schema) |
| PROTOCOL_MISMATCH | no | Subtask does not match agreed `protocol_id` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 90 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

Publishes work items to `A2A_MESSAGE_BUS_REF`; enforces `POLICY_GATE_REF` on `inputs_ref` classifications. Retries are idempotent per `idempotency_key`. Does not embed large payloads inline—only references.
