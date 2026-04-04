# Tool: `route_ticket`

## Purpose

Assign ticket to a queue, agent group, or downstream automation per **routing rules**.

## Invocation

**Invoke** as `route_ticket`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string | yes | Ticket id |
| `destination` | string | yes | Queue key, e.g. `billing_ops` |
| `reason` | string | yes | Which rule fired |
| `priority` | string | yes | `p1`–`p4` |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `assignment_id` | string | Tracking id |
| `sla_due` | string | ISO-8601 if applicable |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| UNKNOWN_DESTINATION | no | `destination` not in routing table |
| RULE_VIOLATION | no | Route inconsistent with classification constraints |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 20s
- Rate limit: 200 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `UNKNOWN_DESTINATION`
- `RULE_VIOLATION` — destination inconsistent with classification (**constraints**)
