# Tool: `run_test`

## Purpose

Execute one or more generated tests in an isolated runner with timeout.

## Invocation

**Function calling** name: `run_test`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_ids` | array | yes | Ids to run |
| `env` | object | no | Runner env vars |
| `timeout_seconds` | integer | no | Default 300 |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Per-id `{ status, duration_ms, stdout_snippet }` |
| `overall` | string | `passed` \| `failed` \| `error` |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RUNNER_UNAVAILABLE | yes | Isolated runner pool exhausted or offline |
| TIMEOUT | yes | Test execution exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 300s (overridable via `timeout_seconds`)
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes (re-run may produce fresh results; use key to dedupe identical batch requests)
- Duplicate detection window: 120s

## Errors

- `RUNNER_UNAVAILABLE`
- `TIMEOUT`
