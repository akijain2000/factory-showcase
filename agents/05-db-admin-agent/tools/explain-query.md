# Tool: `explain_query`

## Purpose

Return execution plan and optimizer estimates for a statement (typically SELECT/UPDATE/DELETE shape) **without** executing mutating effects when possible (`EXPLAIN`).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["sql"],
  "properties": {
    "sql": { "type": "string", "maxLength": 10000 },
    "params": { "type": "array" },
    "analyze": { "type": "boolean", "default": false, "description": "EXPLAIN ANALYZE if policy allows" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "plan_text": "Seq Scan on large_table ...",
  "warnings": ["Seq scan may be expensive at production row counts"]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| POLICY_DENY | no | `analyze: true` not allowed by profile |
| SYNTAX_ERROR | no | SQL could not be parsed |
| CONNECTION_FAILED | yes | Database unreachable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

`analyze: true` may execute the query on some engines—**gated** by profile.

## Errors

`POLICY_DENY` if `analyze` not allowed.
