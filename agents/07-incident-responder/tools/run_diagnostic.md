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

## Errors

- `ROUTINE_NOT_ALLOWED` — violates **constraints**
- `ROUTINE_FAILED`
