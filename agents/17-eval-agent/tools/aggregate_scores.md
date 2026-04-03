# Tool: `aggregate_scores`

## Purpose

Combine multiple per-trajectory score records into cohort statistics and pass/fail gates.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["rubric_id", "score_record_refs", "aggregation"],
  "properties": {
    "rubric_id": { "type": "string" },
    "score_record_refs": {
      "type": "array",
      "minItems": 1,
      "maxItems": 5000,
      "items": { "type": "string" }
    },
    "aggregation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["method"],
      "properties": {
        "method": {
          "type": "string",
          "enum": ["mean", "trimmed_mean", "worst_dimension", "percentile"]
        },
        "trim_percent": { "type": "number", "minimum": 0, "maximum": 0.4 },
        "percentile": { "type": "number", "minimum": 0, "maximum": 100 },
        "gate": {
          "type": "object",
          "properties": {
            "min_mean": { "type": "number" },
            "min_per_dimension": { "type": "object" }
          }
        }
      }
    }
  }
}
```

## Return shape

```json
{
  "rubric_id": "rb_01JQZ",
  "n": 120,
  "aggregate": {
    "mean": { "correctness": 0.79, "tool_discipline": 0.71 },
    "worst_dimension": "tool_discipline"
  },
  "gate": { "passed": false, "failed_reasons": ["tool_discipline below min"] },
  "outliers": []
}
```

## Side effects

- Writes **cohort report** artifact for dashboards.
- May trigger webhooks when `gate.passed` is false.
