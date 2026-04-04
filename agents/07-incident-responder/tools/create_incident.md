# Tool: `create_incident`

## Purpose

Open a durable incident record with timeline slots for postmortem.

## Invocation

**MCP** / function name: `create_incident`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Incident title |
| `severity` | string | yes | `sev1`–`sev4` |
| `affected_services` | array | yes | Service names |
| `summary` | string | yes | Current understanding |
| `links` | array | no | Dashboards, queries |
| `idempotency_key` | string (uuid) | no | Dedupe key for incident creation |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | string | Ticket id |
| `url` | string | Human link |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| DUPLICATE_INCIDENT | no | Merge with existing incident instead |
| TICKETING_UNAVAILABLE | yes | Incident system API error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 20s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 3600s

## Errors

- `DUPLICATE_INCIDENT` — merge instead
