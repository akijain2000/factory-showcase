# Tool: `audit_log`

## Purpose

Record tamper-evident security and compliance events with minimal sensitive content: decision codes, fingerprints, tool names, and correlation ids.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["event_type", "severity", "correlation_id"],
  "properties": {
    "event_type": {
      "type": "string",
      "enum": [
        "input_sanitized",
        "injection_detected",
        "permission_check",
        "output_validation",
        "tool_invocation",
        "session_terminated"
      ]
    },
    "severity": {
      "type": "string",
      "enum": ["info", "low", "medium", "high", "critical"]
    },
    "correlation_id": { "type": "string", "maxLength": 256 },
    "actor": {
      "type": "object",
      "properties": {
        "subject": { "type": "string" },
        "tenant_id": { "type": "string" }
      }
    },
    "details": {
      "type": "object",
      "description": "Redacted key/value bag; no raw secrets."
    },
    "related_fingerprints": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 20
    },
    "audit_event_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "appended": true,
  "sequence": 918221,
  "chain_tip": "hmac-sha256:..."
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| APPEND_FAILED | yes | Audit storage write rejected or transient error |
| STORAGE_QUOTA | no | Tenant or stream quota exceeded |
| CHAIN_VERIFICATION_FAILED | no | Tamper-evident chain could not be extended |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 1000 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `audit_event_id` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 604800s

## Side effects

- **Append-only** write to audit storage; replication latency depends on backend.
- High-severity events may trigger SIEM forwarders or paging policies.
