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

## Errors

- `OPERATION_NOT_FOUND`
