# Tool: `execute_ddl`

## Purpose

Apply a **single** DDL statement after **HITL** approval and policy checks.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["ddl", "approval_id", "idempotency_key"],
  "properties": {
    "ddl": { "type": "string", "maxLength": 10000 },
    "approval_id": { "type": "string", "description": "Short-lived token from ticketing/HITL system" },
    "idempotency_key": { "type": "string", "format": "uuid" },
    "backup_id": { "type": "string", "description": "From backup_table when policy requires" },
    "expected_lock_timeout_ms": { "type": "integer", "default": 3000 }
  }
}
```

## Preconditions (runtime-enforced)

1. `approval_id` validates against HITL service and matches session tenant.
2. DDL parse tree allowlisted (no `DROP DATABASE`, etc., unless break-glass role).
3. If policy demands, `backup_id` present and not expired.

## Return shape

```json
{
  "ok": true,
  "applied": true,
  "statement_tag": "ALTER TABLE",
  "duration_ms": 120
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| HITL_REQUIRED | no | Missing or invalid `approval_id` |
| POLICY_DENY | no | Violates sandbox or forbidden verb |
| BACKUP_REQUIRED | no | Policy requires valid `backup_id` |
| LOCK_TIMEOUT | yes | Could not acquire lock in time |
| DDL_SYNTAX_ERROR | no | Parse tree rejected |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 300s
- Rate limit: 15 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (required field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Errors

| `code` | Meaning |
|--------|---------|
| `HITL_REQUIRED` | Missing/invalid approval |
| `POLICY_DENY` | Violates sandbox or forbidden verb |
| `BACKUP_REQUIRED` | Policy needs backup_id |
| `LOCK_TIMEOUT` | Could not acquire lock in time |

## Side effects

**Schema mutation** on the target database.
