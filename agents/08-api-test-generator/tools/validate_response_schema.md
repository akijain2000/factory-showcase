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

## Errors

- `TEST_NOT_FOUND`
