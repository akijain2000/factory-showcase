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
    }
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

## Side effects

- **Append-only** write to audit storage; replication latency depends on backend.
- High-severity events may trigger SIEM forwarders or paging policies.
