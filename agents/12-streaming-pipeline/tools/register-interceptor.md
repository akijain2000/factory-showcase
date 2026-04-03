# Tool: `register_interceptor`

## Purpose

Attach an ordered middleware hook to the pipeline for a given topic pattern or global scope. Used for enrichment, policy, metrics, and transforms.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["name", "phase", "order_key", "handler_ref"],
  "properties": {
    "name": { "type": "string", "maxLength": 128 },
    "topic_pattern": { "type": "string", "maxLength": 256 },
    "phase": {
      "type": "string",
      "enum": ["ingress", "pre_dispatch", "post_dispatch"]
    },
    "order_key": { "type": "string", "maxLength": 64 },
    "handler_ref": {
      "type": "string",
      "description": "Deployed function/worker id",
      "maxLength": 256
    },
    "idempotent": { "type": "boolean", "default": true },
    "timeout_ms": { "type": "integer", "minimum": 1, "maximum": 600000, "default": 5000 },
    "max_concurrency": { "type": "integer", "minimum": 1, "maximum": 10000, "default": 64 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "registration_id": "icp_7pQm01",
  "effective_order": ["metrics", "pii_redact", "rate_limit", "enrich"],
  "warnings": []
}
```

## Side effects

Updates live routing table version; rolling deploy may require **dual-register** during cutover. Records audit entry with principal. Misordered cycles are rejected with `ORDERING_CONFLICT` without applying changes.
