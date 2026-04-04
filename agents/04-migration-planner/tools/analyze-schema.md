# Tool: `analyze_schema`

## Purpose

Return structured description of tables, columns, indexes, and constraints relevant to a migration scope.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["scope"],
  "properties": {
    "scope": {
      "type": "object",
      "properties": {
        "schemas": { "type": "array", "items": { "type": "string" } },
        "tables": { "type": "array", "items": { "type": "string" } }
      }
    },
    "include_stats": { "type": "boolean", "default": false }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "tables": [
    {
      "schema": "public",
      "name": "orders",
      "columns": [{ "name": "id", "type": "uuid", "nullable": false }],
      "indexes": ["orders_pkey"]
    }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CONNECTION_FAILED | yes | Catalog DB unreachable |
| SCOPE_EMPTY | no | No tables matched `scope` |
| STATS_UNAVAILABLE | yes | Extended stats query failed |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 50
- Cursor-based: returns `next_cursor` in response
- Max results per call: 500

## Side effects

Read-only metadata queries.
