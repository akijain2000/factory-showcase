# Tool: `backup_table`

## Purpose

Create a restorable snapshot or logical export for a table prior to DDL (implementation: pg_dump slice, storage snapshot, or replica flashback—documented per org).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema", "table"],
  "properties": {
    "schema": { "type": "string" },
    "table": { "type": "string" },
    "method": {
      "type": "string",
      "enum": ["logical", "snapshot"],
      "default": "logical"
    },
    "retention_hours": { "type": "integer", "minimum": 1, "maximum": 168, "default": 24 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "backup_id": "bak-9c21",
  "location_ref": "s3://redacted/backup_id",
  "expires_at": "2026-04-05T12:00:00Z"
}
```

## Side effects

Creates backup artifacts; may impact IO.

## Auth

Requires backup role credentials; audited.
