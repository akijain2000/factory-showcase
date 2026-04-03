# Tool: `check_permissions`

## Purpose

Authorize a proposed tool invocation using ABAC/RBAC policy: principal attributes, resource scope, data classification, and time-bound roles.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["principal", "tool", "resource_scope"],
  "properties": {
    "principal": {
      "type": "object",
      "required": ["subject", "tenant_id"],
      "properties": {
        "subject": { "type": "string" },
        "tenant_id": { "type": "string" },
        "roles": { "type": "array", "items": { "type": "string" } },
        "clearance": { "type": "string", "enum": ["low", "medium", "high"] }
      }
    },
    "tool": { "type": "string", "maxLength": 128 },
    "resource_scope": {
      "type": "object",
      "properties": {
        "dataset": { "type": "string" },
        "env": { "type": "string", "enum": ["dev", "staging", "prod"] },
        "labels": { "type": "object" }
      }
    },
    "justification": { "type": "string", "maxLength": 2000 }
  }
}
```

## Return shape

```json
{
  "decision": "deny",
  "reason_code": "ENV_MISMATCH",
  "matched_policy": "prod_tools_require_breakglass",
  "expires_at_ms": null
}
```

## Side effects

- Writes **authorization decision** to audit sink (allow/deny).
- May mint a short-lived **elevation token** for allow decisions that require step-up (integrator-specific).
