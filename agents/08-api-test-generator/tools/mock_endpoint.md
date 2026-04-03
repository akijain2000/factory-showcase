# Tool: `mock_endpoint`

## Purpose

Register a stub server or wiremock mapping for external dependencies during tests.

## Invocation

**Function calling** name: `mock_endpoint`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Mock suite name |
| `method` | string | yes | HTTP method |
| `path_pattern` | string | yes | Path or regex |
| `response` | object | yes | Status, headers, body |
| `priority` | integer | no | Disambiguation |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `mock_id` | string | Id for teardown |
| `base_url` | string | Where clients should send traffic |

## Errors

- `MOCK_REGISTRY_FULL`
- `CONFLICTING_MAPPING`
