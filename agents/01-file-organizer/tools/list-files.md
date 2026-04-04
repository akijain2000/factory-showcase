# Tool: `list_files`

## Purpose

List files and directories under a path relative to the agent root, with optional filtering by extension or modified date.

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
      "description": "Directory path relative to workspace root."
    },
    "recursive": {
      "type": "boolean",
      "default": false,
      "description": "If true, list recursively."
    },
    "extensions": {
      "type": "array",
      "items": { "type": "string", "pattern": "^\\.?[A-Za-z0-9]+$" },
      "description": "Optional filter; e.g. [\".pdf\", \"md\"]."
    },
    "modified_after": {
      "type": "string",
      "format": "date-time",
      "description": "Optional ISO 8601 lower bound on mtime."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "entries": [
    { "name": "report.pdf", "type": "file", "size": 1024, "mtime": "2026-04-01T12:00:00Z" }
  ]
}
```

Error:

```json
{
  "ok": false,
  "error": { "code": "PATH_OUTSIDE_ROOT", "message": "...", "retryable": false }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PATH_OUTSIDE_ROOT | no | Path escapes workspace root |
| IO_ERROR | yes | Transient filesystem read failure |
| TIMEOUT | yes | Directory walk exceeded time limit |
| INVALID_INPUT | no | Malformed arguments or invalid filter |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 200
- Cursor-based: returns `next_cursor` in response
- Max results per call: 2000

## Side effects

None (read-only).

## Auth / permissions

Requires read access within `FILE_ORGANIZER_ROOT`.
