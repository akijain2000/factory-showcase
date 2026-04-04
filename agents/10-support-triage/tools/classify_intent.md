# Tool: `classify_intent`

## Purpose

Produce normalized intent labels and confidence for a support ticket.

## Invocation

**Function calling** name: `classify_intent`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticket_id` | string | yes | External id |
| `subject` | string | yes | Ticket subject |
| `body` | string | yes | Plain text body |
| `channel` | string | no | `email` \| `chat` \| `web` |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `classification` | object | Same fields as prompt JSON schema |
| `model_version` | string | For audit |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| TICKET_TOO_LARGE | no | Input exceeds size limits (truncation applied) |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 100 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `TICKET_TOO_LARGE` — truncate with marker
