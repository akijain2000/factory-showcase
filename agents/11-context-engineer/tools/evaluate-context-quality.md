# Tool: `evaluate_context_quality`

## Purpose

Score a curated (or compressed) bundle for **coverage**, **grounding**, **redundancy**, and **constraint visibility** before expensive generation or prompt promotion.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["objective"],
  "properties": {
    "curated_bundle_id": { "type": "string", "maxLength": 128 },
    "inline_bundle": {
      "type": "object",
      "description": "Optional when bundle_id not yet persisted",
      "additionalProperties": true
    },
    "objective": { "type": "string", "maxLength": 8000 },
    "thresholds": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "min_coverage": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.72 },
        "max_redundancy": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.35 },
        "min_constraint_visibility": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.9 }
      }
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "scores": {
    "coverage": 0.78,
    "grounding": 0.81,
    "redundancy": 0.22,
    "constraint_visibility": 0.95
  },
  "pass": true,
  "gaps": ["Missing explicit API error code mapping for 429 handling."],
  "estimated_tokens": 5100
}
```

## Side effects

Read-only against bundle content; may write **ephemeral** evaluation cache keyed by `(bundle_id, objective_hash)` with TTL. No user-visible mutation of prompts or bundles.
