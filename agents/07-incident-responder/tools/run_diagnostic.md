# Tool: `run_diagnostic`

## Purpose

Execute allowlisted diagnostic routines (read-only or explicitly approved).

## Invocation

**Invoke** as `run_diagnostic`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `routine` | string | yes | Registered routine id |
| `params` | object | no | Routine-specific parameters |
| `correlation_id` | string | no | Trace across tools |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | `pass` \| `fail` \| `inconclusive` |
| `details` | object | Structured findings |
| `artifacts` | array | Links to captures |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| ROUTINE_NOT_ALLOWED | no | Routine violates policy **constraints** |
| ROUTINE_FAILED | yes | Routine exited with failure (may retry) |
| ROUTINE_UNKNOWN | no | Unregistered `routine` id |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 300s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `ROUTINE_NOT_ALLOWED` — violates **constraints**
- `ROUTINE_FAILED`
