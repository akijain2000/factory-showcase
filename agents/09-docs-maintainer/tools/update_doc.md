# MCP Tool: `update_doc`

## Purpose

Apply a documentation patch atomically with optional front-matter merge.

## Invocation

**Invoke** as `update_doc` through **MCP** or hosted **function calling**.

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | yes | Doc path under docs/ or README |
| `patch` | string | yes | Unified diff or structured ops JSON |
| `rationale` | string | yes | Why the change (for audit) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `applied` | boolean | Success flag |
| `new_sha256` | string | Post-patch hash |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PATCH_CONFLICT | no | Patch does not apply cleanly to current content |
| RATIONALE_MISSING | no | Required audit rationale absent |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes (same key + patch yields same `new_sha256`)
- Duplicate detection window: 300s

## Errors

- `PATCH_CONFLICT`
- `RATIONALE_MISSING` — enforced by **rules**
