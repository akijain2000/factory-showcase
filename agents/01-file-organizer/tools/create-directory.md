# Tool: `create_directory`

## Purpose

Create a directory relative to the workspace root. Creates parent directories when needed (`mkdir -p` semantics).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["path"],
  "properties": {
    "path": {
      "type": "string",
      "description": "Directory path relative to root."
    },
    "mode": {
      "type": "string",
      "pattern": "^0[0-7]{3}$",
      "description": "Optional Unix mode string e.g. \"0755\"."
    },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key for safe retries."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "result": { "path": "by-date/2026/04", "created": true }
}
```

If the directory already exists:

```json
{
  "ok": true,
  "result": { "path": "by-date/2026/04", "created": false }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PATH_OUTSIDE_ROOT | no | Path escapes `FILE_ORGANIZER_ROOT` |
| INVALID_PATH | no | Malformed or empty path segment |
| PERMISSION_DENIED | no | Insufficient access |
| DISK_FULL | no | Filesystem has no space |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 300s

## Side effects

Creates zero or more directories.

## Auth / permissions

Write access within `FILE_ORGANIZER_ROOT`.
