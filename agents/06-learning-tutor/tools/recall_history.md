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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RATE_LIMITED | yes | Reduce `limit` or wait |
| LEARNER_NOT_FOUND | no | Unknown `learner_id` |
| STORE_UNAVAILABLE | yes | Episodic backend transient failure |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 20s
- Rate limit: 90 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 20
- Cursor-based: returns `next_cursor` in response
- Max results per call: 100

## Errors

- `RATE_LIMITED` — reduce `limit` or wait
