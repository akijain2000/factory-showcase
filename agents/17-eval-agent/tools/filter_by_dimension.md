# Tool: `filter_by_dimension`

## Purpose

Filter trajectory **spans** by rubric dimension relevance so downstream aggregation is not dominated by irrelevant verbosity.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["trajectory_ref", "rubric_id", "policy"],
  "properties": {
    "trajectory_ref": { "type": "string" },
    "rubric_id": { "type": "string" },
    "policy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mode"],
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["keep_top_k_per_dimension", "drop_below_threshold", "manual_span_ids"]
        },
        "top_k": { "type": "integer", "minimum": 1, "maximum": 50 },
        "relevance_threshold": { "type": "number", "minimum": 0, "maximum": 1 },
        "span_ids": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

## Return shape

```json
{
  "filtered_ref": "tr_884b_f1",
  "kept_span_ids": ["t5", "t12", "t18"],
  "dropped": [{ "span_id": "t7", "reason": "low_relevance" }],
  "provenance": { "policy": "keep_top_k_per_dimension", "top_k": 5 }
}
```

## Side effects

- Creates a **derived view** of the trajectory (non-destructive) in storage.
- Logs filter statistics for monitoring rubric drift and verbosity.
