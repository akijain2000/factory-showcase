# Tool: `parse_openapi`

## Purpose

Ingest OpenAPI 3.x JSON/YAML and return normalized operations + component schemas.

## Invocation

**Function calling** name: `parse_openapi`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | URL or filesystem path |
| `format` | string | no | `json` \| `yaml` (auto-detect if omitted) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | OpenAPI version |
| `operations` | array | `{ operation_id, method, path, security, request_body, responses }` |
| `schemas` | object | Resolved component map (refs inlined or pointers) |
| `warnings` | array | Non-fatal parse issues |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| INVALID_OPENAPI | no | Document failed structural or semantic validation |
| UNRESOLVABLE_REF | no | `$ref` could not be resolved |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `INVALID_OPENAPI`
- `UNRESOLVABLE_REF`
