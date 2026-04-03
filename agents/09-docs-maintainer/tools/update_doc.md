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

## Errors

- `PATCH_CONFLICT`
- `RATIONALE_MISSING` — enforced by **rules**
