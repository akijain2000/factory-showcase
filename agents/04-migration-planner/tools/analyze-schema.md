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

## Side effects

Read-only metadata queries.
