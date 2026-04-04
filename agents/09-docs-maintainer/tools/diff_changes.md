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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| INVALID_REF | no | Unknown git ref in `base` or `head` |
| DIRTY_WORKTREE | yes | Ambiguous diff when worktree has local changes |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `INVALID_REF`
- `DIRTY_WORKTREE` — warn when ambiguous
