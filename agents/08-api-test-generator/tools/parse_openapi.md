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

## Errors

- `INVALID_OPENAPI`
- `UNRESOLVABLE_REF`
