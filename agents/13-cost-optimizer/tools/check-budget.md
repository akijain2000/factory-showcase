# Tool: `check_budget`

## Purpose

Evaluate remaining budget for a scope and return **allow**, **downgrade**, or **halt** with headroom metrics.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["scope", "projected_increment_usd"],
  "properties": {
    "scope": {
      "type": "object",
      "additionalProperties": false,
      "required": ["tenant_id"],
      "properties": {
        "tenant_id": { "type": "string", "maxLength": 64 },
        "project_id": { "type": "string", "maxLength": 64 },
        "team_id": { "type": "string", "maxLength": 64 }
      }
    },
    "projected_increment_usd": { "type": "number", "minimum": 0 },
    "window": {
      "type": "string",
      "enum": ["daily", "monthly", "per_request_cap"],
      "default": "daily"
    },
    "enforce": { "type": "boolean", "default": true }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "action": "allow",
  "headroom_usd": 58.12,
  "spent_usd": 241.88,
  "cap_usd": 300,
  "retry_after_sec": null
}
```

## Side effects

May write a **budget check** audit record with hashed scope ids. If `enforce: false`, returns advisory values only and does not mutate breaker state. On `halt`, may publish notification webhook per FinOps policy.
