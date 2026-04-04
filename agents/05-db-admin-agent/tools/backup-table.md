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
    "retention_hours": { "type": "integer", "minimum": 1, "maximum": 168, "default": 24 },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key for backup job submission."
    }
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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| TABLE_NOT_FOUND | no | Schema or table does not exist |
| STORAGE_QUOTA | no | Backup destination full |
| SNAPSHOT_FAILED | yes | Storage provider transient error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 3600s
- Rate limit: 6 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 3600s

## Side effects

Creates backup artifacts; may impact IO.

## Auth

Requires backup role credentials; audited.
