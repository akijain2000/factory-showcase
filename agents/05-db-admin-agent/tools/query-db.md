# Tool: `query_db`

## Purpose

Run a **single** SQL statement constrained by deployment profile (e.g. SELECT-only).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["sql"],
  "properties": {
    "sql": {
      "type": "string",
      "maxLength": 10000,
      "description": "Parameterized SQL; no multiple statements."
    },
    "params": {
      "type": "array",
      "description": "Positional or named parameters per driver mapping"
    },
    "timeout_ms": { "type": "integer", "minimum": 100, "maximum": 60000, "default": 5000 },
    "max_rows": { "type": "integer", "minimum": 1, "maximum": 10000, "default": 1000 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "columns": ["id", "status"],
  "rows": [["a1", "active"]],
  "truncated": false
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| POLICY_DENY | no | Non-SELECT or forbidden statement class |
| SYNTAX_ERROR | no | SQL parse or bind error |
| QUERY_TIMEOUT | yes | Statement exceeded `timeout_ms` |
| CONNECTION_FAILED | yes | Pool or network error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s (caller may set `timeout_ms` up to 60s)
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 1000
- Cursor-based: returns `next_cursor` in response
- Max results per call: 10000

## Policy enforcement

Runtime MUST reject non-SELECT in RO profile.

## Errors

`POLICY_DENY`, `TIMEOUT`, `SYNTAX_ERROR`.
