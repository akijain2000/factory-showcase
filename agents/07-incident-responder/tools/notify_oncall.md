# Tool: `notify_oncall`

## Purpose

Notify the on-call rotation with severity, summary, and deep links.

## Invocation

**Function calling** name: `notify_oncall`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `severity` | string | yes | `sev1`–`sev4` |
| `title` | string | yes | Short title |
| `body` | string | yes | Markdown body with impact + next steps |
| `incident_id` | string | no | If `create_incident` already ran |
| `channels` | array | no | `["pager", "slack"]` etc. |
| `idempotency_key` | string (uuid) | no | Dedupe key for notification fan-out |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `notification_id` | string | Delivery id |
| `delivered` | boolean | Ack from at least one channel |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| ESCALATION_POLICY_MISSING | no | No routing policy for team or severity |
| CHANNEL_UNAVAILABLE | yes | Pager/Slack provider error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 20 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `ESCALATION_POLICY_MISSING`
