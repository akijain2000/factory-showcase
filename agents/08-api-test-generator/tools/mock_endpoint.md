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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| MOCK_REGISTRY_FULL | no | Stub registry capacity exhausted |
| CONFLICTING_MAPPING | no | Overlapping or ambiguous mock mapping |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 300s

## Errors

- `MOCK_REGISTRY_FULL`
- `CONFLICTING_MAPPING`
