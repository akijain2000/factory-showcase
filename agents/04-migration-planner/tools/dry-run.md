# Tool: `dry_run`

## Purpose

Validate a single `step_id` without committing (transaction rollback, terraform plan, kubectl diff).

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
    "verbose": { "type": "boolean", "default": true }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "step_id": "s1",
  "plan_summary": "Will add column with default; table rewrite estimated 2m",
  "warnings": ["Large table: consider batched backfill"]
}
```

## Side effects

None on production data when implemented with rolled-back transaction or pure plan mode.

## Errors

`STEP_NOT_FOUND`, `PLAN_FAILED` (not retryable until plan fixed).
