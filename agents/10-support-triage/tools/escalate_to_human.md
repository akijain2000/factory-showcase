# Tool: `escalate_to_human`

## Purpose

Hand ticket to a human with structured summary for the queue owner.

## Invocation

**MCP** / **function calling** name: `escalate_to_human`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string | yes | Ticket id |
| `reason` | string | yes | Why automation stopped |
| `summary` | string | yes | Bullet-style facts only |
| `severity` | string | no | Mirrors urgency |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `handoff_id` | string | Id for CRM |
| `assigned_team` | string | Human queue |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| ALREADY_ESCALATED | no | Ticket already in human queue |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `ALREADY_ESCALATED`
