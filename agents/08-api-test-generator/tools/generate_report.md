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

## Errors

- `RUN_ID_UNKNOWN`
