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

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `notification_id` | string | Delivery id |
| `delivered` | boolean | Ack from at least one channel |

## Errors

- `ESCALATION_POLICY_MISSING`
