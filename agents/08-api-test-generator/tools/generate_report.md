# Tool: `generate_report`

## Purpose

Aggregate `run_test` outcomes into Markdown/HTML/JUnit for CI.

## Invocation

**Invoke** as `generate_report`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `run_id` | string | yes | Correlation id from test run |
| `format` | string | yes | `markdown` \| `html` \| `junit` |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `artifact_path` | string | Written file location |
| `summary` | object | Counts, slowest tests, flake hints |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RUN_ID_UNKNOWN | no | No test run found for `run_id` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `run_id` (optional field in arguments; same `run_id` overwrites idempotently)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `RUN_ID_UNKNOWN`
