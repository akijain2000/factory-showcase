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
| `idempotency_key` | string (uuid) | no | Dedupe key for safe retries |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Episodic record id |
| `updated_mastery` | number | New coarse mastery for topic |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| WRITE_CONFLICT | yes | Optimistic concurrency conflict |
| LEARNER_NOT_FOUND | no | Unknown `learner_id` |
| TOPIC_UNKNOWN | no | Invalid topic code |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `WRITE_CONFLICT` — retry with backoff
