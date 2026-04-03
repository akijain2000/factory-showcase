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

## Errors

- `ALREADY_ESCALATED`
