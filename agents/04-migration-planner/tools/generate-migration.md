# Tool: `generate_migration`

## Purpose

Generate migration artifacts: ordered forward operations each with matching rollback and a stable `step_id`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["intent", "dialect"],
  "properties": {
    "intent": { "type": "string", "description": "Natural language + constraints" },
    "dialect": { "type": "string", "enum": ["postgres", "mysql", "sqlite", "terraform", "kubernetes"] },
    "safety": {
      "type": "string",
      "enum": ["online", "locking_ok", "maintenance_window"],
      "default": "online"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "migration_id": "mgr-20260404-01",
  "steps": [
    {
      "step_id": "s1",
      "forward": "ALTER TABLE ...",
      "rollback": "ALTER TABLE ...",
      "depends_on": []
    }
  ]
}
```

## Side effects

Writes migration files or records in migration registry (implementation-defined).
