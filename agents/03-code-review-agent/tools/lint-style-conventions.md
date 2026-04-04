# Tool: `lint_style_conventions` (style_reviewer)

## Purpose

Run configured style rules (naming, import order, formatting drift vs project guide).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["path"],
  "properties": {
    "path": { "type": "string", "description": "File path in repo" },
    "ruleset": { "type": "string", "description": "e.g. ruff, eslint, internal" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "violations": [
    { "line": 3, "code": "N801", "message": "Class names should use CapWords" }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| LINTER_CRASH | yes | Subprocess exited unexpectedly |
| RULESET_UNKNOWN | no | `ruleset` not configured |
| PATH_NOT_FOUND | no | File or directory missing |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

May invoke local linter subprocess (sandboxed).
