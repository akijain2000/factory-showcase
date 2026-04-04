# Tool: `generate_response`

## Purpose

Draft a customer-facing reply using KB hits and classification (no new factual claims).

## Invocation

**Function calling** name: `generate_response`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string | yes | Ticket id |
| `tone` | string | no | `empathetic_brief` \| `technical_detailed` |
| `kb_article_ids` | array | no | Citations to prefer |
| `classification` | object | yes | From `classify_intent` |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `draft` | string | Email/chat body |
| `citations_used` | array | Article ids actually referenced |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| MISSING_GROUNDING | no | Insufficient KB grounding for factual claims |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes (same key returns same draft hash)
- Duplicate detection window: 300s

## Errors

- `MISSING_GROUNDING` — no KB for factual claims; require **escalation** path
