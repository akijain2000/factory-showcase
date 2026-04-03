# Tool: `negotiate_protocol`

## Purpose

Align participating agents on **schemas**, **error codes**, **idempotency**, and **security bindings**, producing a durable `protocol_id`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["peer_agent_ids", "payload_schema_ref"],
  "properties": {
    "peer_agent_ids": {
      "type": "array",
      "items": { "type": "string", "maxLength": 256 },
      "minItems": 1,
      "maxItems": 16
    },
    "payload_schema_ref": { "type": "string", "maxLength": 512 },
    "error_schema_ref": { "type": "string", "maxLength": 512 },
    "auth_binding": {
      "type": "string",
      "enum": ["mtls", "oauth_client_credentials", "ephemeral_delegate_token"],
      "default": "ephemeral_delegate_token"
    },
    "sla_ms": { "type": "integer", "minimum": 100, "maximum": 3600000 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "protocol_id": "proto_8Lm2nQ",
  "agreed_schema_hash": "sha256:91af…",
  "participants": ["coordinator", "svc/code-analyzer@v3"],
  "notes": ["Error model maps TOOL_TIMEOUT to retryable=true."]
}
```

## Side effects

Registers protocol record on `A2A_MESSAGE_BUS_REF` metadata service; may issue short-lived **delegate token** handles (not raw secrets) when `auth_binding` requires it. Fails with `SCHEMA_MISMATCH` if any peer rejects.
