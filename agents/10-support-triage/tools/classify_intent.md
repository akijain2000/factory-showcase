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

## Errors

- `TICKET_TOO_LARGE` — truncate with marker
