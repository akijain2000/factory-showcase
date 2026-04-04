# Tool: `generate_exercise`

## Purpose

Create a single practice item aligned to learner level and known gaps.

## Invocation

**Function calling** name: `generate_exercise`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learner_id` | string | yes | Learner id |
| `topic` | string | yes | Topic code |
| `difficulty` | number | yes | 0.0–1.0 target difficulty |
| `format` | string | no | `mcq` \| `short_answer` \| `worked_steps` |
| `avoid_patterns` | array | no | Patterns to avoid (from episodic memory) |
| `idempotency_key` | string (uuid) | no | Dedupe key for safe retries |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `exercise_id` | string | Unique id for later `store_progress` |
| `prompt` | string | Learner-facing question |
| `rubric` | object | Optional grading hints (not shown to learner) |
| `expected_time_minutes` | number | Estimated effort |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| DIFFICULTY_OUT_OF_RANGE | no | `difficulty` outside 0.0–1.0 |
| TOPIC_LOCKED | no | Prerequisite not met |
| MODEL_UNAVAILABLE | yes | Generator backend transient failure |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 300s

## Errors

- `DIFFICULTY_OUT_OF_RANGE`
- `TOPIC_LOCKED` — prerequisite not met
