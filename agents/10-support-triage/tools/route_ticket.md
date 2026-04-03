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

## Errors

- `UNKNOWN_DESTINATION`
- `RULE_VIOLATION` — destination inconsistent with classification (**constraints**)
