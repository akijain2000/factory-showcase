# Tool: `generate_test_case`

## Purpose

Emit source code + metadata for one API test from a parsed operation.

## Invocation

**Invoke** as `generate_test_case`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operation_id` | string | yes | From parse output |
| `framework` | string | yes | e.g. `pytest_requests`, `k6` |
| `base_url_var` | string | no | Env var name for host |
| `fixtures` | object | no | Named fixture payloads |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `test_id` | string | Stable id |
| `files` | array | `{ path, content }` |
| `dependencies` | array | Other `test_id`s or mocks needed |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| OPERATION_NOT_FOUND | no | `operation_id` not in parsed spec |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 90 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Errors

- `OPERATION_NOT_FOUND`
