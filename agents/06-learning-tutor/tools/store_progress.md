# Tool: `store_progress`

## Purpose

Append an **episodic** learning event and update **semantic** aggregates (mastery estimates).

## Invocation

**MCP / function** name: `store_progress`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learner_id` | string | yes | Learner id |
| `exercise_id` | string | no | From `generate_exercise` if applicable |
| `topic` | string | yes | Topic code |
| `outcome` | string | yes | `correct` \| `partial` \| `incorrect` \| `skipped` |
| `latency_ms` | integer | no | Response time |
| `hints_used` | integer | no | Count of hints |
| `notes` | string | no | Short free-text (misconception, emotion cue) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Episodic record id |
| `updated_mastery` | number | New coarse mastery for topic |

## Errors

- `WRITE_CONFLICT` — retry with backoff
