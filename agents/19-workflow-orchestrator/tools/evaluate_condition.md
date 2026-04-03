# Tool: `evaluate_condition`

## Purpose

Evaluate a **named branching expression** against structured `facts` produced by prior steps; returns a discrete decision for edge selection.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["expression_ref", "facts"],
  "properties": {
    "expression_ref": {
      "type": "string",
      "description": "Registry key for approved expression bundle (CEL/Rego/etc.)."
    },
    "facts": {
      "type": "object",
      "description": "JSON-serializable fact map; must not include secrets."
    },
    "expected_type": {
      "type": "string",
      "enum": ["boolean", "enum", "number"],
      "default": "boolean"
    },
    "enum_labels": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 32
    }
  }
}
```

## Return shape

```json
{
  "value": true,
  "branch": "approve_path",
  "trace": [{ "rule": "amount_within_limit", "result": true }],
  "duration_ms": 3
}
```

## Side effects

- Logs **expression_ref** + outcome to workflow audit (facts redacted).
- Caches compiled expression where supported to reduce latency.
