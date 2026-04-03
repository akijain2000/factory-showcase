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

## Side effects

`analyze: true` may execute the query on some engines—**gated** by profile.

## Errors

`POLICY_DENY` if `analyze` not allowed.
