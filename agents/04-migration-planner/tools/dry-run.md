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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| STEP_NOT_FOUND | no | Unknown `migration_id` or `step_id` |
| PLAN_FAILED | no | Validator rejected plan until fixed |
| PROVIDER_ERROR | yes | Terraform/kubectl/plan backend transient failure |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 600s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

None on production data when implemented with rolled-back transaction or pure plan mode.

## Errors

`STEP_NOT_FOUND`, `PLAN_FAILED` (not retryable until plan fixed).
