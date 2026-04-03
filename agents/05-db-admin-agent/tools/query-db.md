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

## Policy enforcement

Runtime MUST reject non-SELECT in RO profile.

## Errors

`POLICY_DENY`, `TIMEOUT`, `SYNTAX_ERROR`.
