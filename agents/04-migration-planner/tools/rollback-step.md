# Tool: `rollback_step`

## Purpose

Apply the rollback associated with a previously executed `step_id`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["migration_id", "step_id"],
  "properties": {
    "migration_id": { "type": "string" },
    "step_id": { "type": "string" },
    "reason": { "type": "string", "maxLength": 2000 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "step_id": "s1",
  "rolled_back_at": "2026-04-04T12:05:00Z"
}
```

## Side effects

Reverts the forward step when possible; may require maintenance window for some DDL.

## Errors

`ROLLBACK_UNSUPPORTED`, `DATA_LOSS_RISK` — surface to human operator.
