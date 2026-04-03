# Tool: `calibrate_rubric`

## Purpose

Adjust rubric **weights** or **anchors** using labeled anchor trajectories to align scores with human judgments or a gold evaluator.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["base_rubric_id", "anchors", "objective"],
  "properties": {
    "base_rubric_id": { "type": "string" },
    "anchors": {
      "type": "array",
      "minItems": 5,
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["trajectory_ref", "label"],
        "properties": {
          "trajectory_ref": { "type": "string" },
          "label": { "type": "number", "minimum": 0, "maximum": 1 },
          "weight": { "type": "number", "minimum": 0, "default": 1 }
        }
      }
    },
    "objective": {
      "type": "string",
      "enum": ["minimize_mse", "maximize_spearman", "maximize_agreement_rate"]
    },
    "holdout_refs": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 200
    }
  }
}
```

## Return shape

```json
{
  "calibrated_rubric_id": "rb_01JQZ_c2",
  "revision": 2,
  "delta_weights": { "tool_discipline": 0.07, "communication": -0.02 },
  "metrics": { "spearman": 0.71, "mse": 0.018 },
  "warnings": ["small_anchor_set"]
}
```

## Side effects

- Persists new rubric revision; base rubric remains for replay comparisons.
- Logs calibration job parameters for reproducibility.
