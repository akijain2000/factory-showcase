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

## Errors

- `RUNNER_UNAVAILABLE`
- `TIMEOUT`
