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

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `incident_id` | string | Ticket id |
| `url` | string | Human link |

## Errors

- `DUPLICATE_INCIDENT` — merge instead
