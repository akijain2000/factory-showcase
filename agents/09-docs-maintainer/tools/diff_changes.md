# MCP Tool: `diff_changes`

## Purpose

Summarize code changes between refs or working tree for doc scope control.

## Invocation

**MCP** tool name: `diff_changes`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `base` | string | yes | Git ref or `WORKTREE` |
| `head` | string | yes | Git ref or `WORKTREE` |
| `pathspecs` | array | no | Limit to subtrees |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `files` | array | `{ path, change_kind, hunks_summary }` |
| `stats` | object | Insertions/deletions |

## Errors

- `INVALID_REF`
- `DIRTY_WORKTREE` — warn when ambiguous
