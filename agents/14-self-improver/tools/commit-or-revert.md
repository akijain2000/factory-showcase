# Tool: `commit_or_revert`

## Purpose

Promote a candidate prompt to **active** (`keep`) or discard it (`discard`), updating registry pointers and recording evidence links.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["prompt_id", "candidate_id", "decision"],
  "properties": {
    "prompt_id": { "type": "string", "maxLength": 128 },
    "namespace": { "type": "string", "maxLength": 128, "default": "default" },
    "candidate_id": { "type": "string", "maxLength": 128 },
    "decision": { "type": "string", "enum": ["keep", "discard"] },
    "evidence": {
      "type": "object",
      "description": "Structured pointers to eval + compare artifacts",
      "additionalProperties": true
    },
    "review_ticket_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "decision": "keep",
  "active_version": "2026.04.04-cand-9Lm2",
  "previous_version": "2026.04.03-11",
  "rollback_handle": "rbk_3nQs81"
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| REVIEW_POLICY_VIOLATION | no | Missing or invalid `review_ticket_id` |
| CANDIDATE_NOT_FOUND | no | Unknown `candidate_id` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments; `candidate_id` + `decision` define logical outcome)
- Safe to retry: yes
- Duplicate detection window: 600s

## Side effects

On `keep`, updates production pointer **only** if review policy satisfied (`review_ticket_id` when required). On `discard`, marks candidate **archived**. Notifies subscribers via registry webhook. Always writes audit row with decision rationale codes.
