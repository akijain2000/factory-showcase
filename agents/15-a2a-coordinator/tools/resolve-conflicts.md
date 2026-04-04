# Tool: `resolve_conflicts`

## Purpose

Apply a **deterministic** merge strategy or escalate with structured options when peer outputs conflict.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["conflict_set_id"],
  "properties": {
    "conflict_set_id": { "type": "string", "maxLength": 128 },
    "strategy": {
      "type": "string",
      "enum": [
        "evidence_first",
        "highest_confidence",
        "human_escalation",
        "redelegate_tiebreaker"
      ],
      "default": "evidence_first"
    },
    "tiebreaker_agent_id": { "type": "string", "maxLength": 256 },
    "escalation_ticket_template": { "type": "string", "maxLength": 256 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "resolution": "merged",
  "winner_handles": ["tsk_9pQm01"],
  "rationale": "Selected output citing stack trace + failing test id; other output lacked evidence refs.",
  "escalation_id": null
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CONFLICT_SET_NOT_FOUND | no | Unknown or expired `conflict_set_id` |
| STRATEGY_UNAVAILABLE | no | Requested strategy cannot be applied (e.g. missing tiebreaker agent) |
| ESCALATION_FAILED | yes | Ticketing or escalation backend error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `conflict_set_id` (required; replays return same resolution artifact when strategy unchanged)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

On `human_escalation`, opens ticket with redacted summaries. On `redelegate_tiebreaker`, enqueues a new subtask (counts toward depth policy). Records immutable **resolution artifact** for compliance review.
