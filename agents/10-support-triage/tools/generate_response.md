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

## Errors

- `MISSING_GROUNDING` — no KB for factual claims; require **escalation** path
