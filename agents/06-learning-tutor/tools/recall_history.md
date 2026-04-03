# Tool: `recall_history`

## Purpose

Retrieve **episodic** recent events and/or **semantic** summaries for personalization.

## Invocation

**Invoke** via **function calling** as `recall_history`.

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learner_id` | string | yes | Learner id |
| `topic` | string | no | Filter by topic; omit for cross-topic summary |
| `mode` | string | no | `episodic` \| `semantic` \| `both` (default `both`) |
| `limit` | integer | no | Max episodic events (default 20, max 100) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `episodic_events` | array | Chronological attempt/hint records |
| `semantic_summary` | string | Compressed strengths/gaps narrative |
| `last_session_at` | string (ISO-8601) | Timestamp of last activity |

## Errors

- `RATE_LIMITED` — reduce `limit` or wait
