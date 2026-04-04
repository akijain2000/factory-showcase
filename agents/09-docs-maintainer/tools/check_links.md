# MCP Tool: `check_links`

## Purpose

Validate links in markdown files: relative paths, anchors, optional HTTP HEAD for allowlisted hosts.

## Invocation

**MCP** name: `check_links`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paths` | array | yes | Markdown files or directories |
| `check_external` | boolean | no | Default false |
| `timeout_ms` | integer | no | Per-link cap |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `broken` | array | `{ file, href, reason }` |
| `ok_count` | integer | Valid links |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| TIMEOUT | yes | Per-link or overall check exceeded time limit |
| EXTERNAL_CHECKS_DISABLED | no | External link validation unavailable under current flags |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s (per-link cap via `timeout_ms`)
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `TIMEOUT`
- `EXTERNAL_CHECKS_DISABLED` when `check_external` false and only external links exist
