# Tool: `validate_response_schema`

## Purpose

Verify generated assertions cover the declared response schema for a status code.

## Invocation

**MCP** tool name: `validate_response_schema`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `test_id` | string | yes | Target test |
| `status_code` | string | yes | e.g. `"200"` |
| `schema_ref` | string | yes | JSON pointer or inline schema hash |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `valid` | boolean | Whether coverage is sufficient |
| `gaps` | array | Missing properties or unconstrained types |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| TEST_NOT_FOUND | no | Unknown `test_id` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 200 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `TEST_NOT_FOUND`
