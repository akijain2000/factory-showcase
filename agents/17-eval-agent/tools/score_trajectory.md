# Tool: `score_trajectory`

## Purpose

Scores an agent trajectory (ordered steps: thoughts, tool calls, observations) against a previously generated or registered rubric identified by `rubric_id`. Produces per-dimension scores for auditing and reward modeling.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "trajectory": {
      "type": "array",
      "description": "Ordered list of trajectory steps (role, content, optional tool metadata).",
      "items": {
        "type": "object",
        "properties": {
          "role": { "type": "string", "enum": ["system", "user", "assistant", "tool"] },
          "content": { "type": "string" },
          "metadata": { "type": "object", "additionalProperties": true }
        },
        "required": ["role", "content"],
        "additionalProperties": false
      },
      "minItems": 1
    },
    "rubric_id": {
      "type": "string",
      "description": "Identifier of the rubric to score against.",
      "minLength": 1
    }
  },
  "required": ["trajectory", "rubric_id"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "rubric_id": "rubric_01HZX9K3",
  "scores": [
    {
      "dimension_id": "dim_1",
      "dimension_name": "Factual grounding",
      "score": 0.82,
      "weight": 0.25,
      "rationale": "Two claims lacked explicit citations."
    },
    {
      "dimension_id": "dim_2",
      "dimension_name": "Task completeness",
      "score": 0.95,
      "weight": 0.2,
      "rationale": "All numbered questions received a direct answer."
    }
  ],
  "aggregate": {
    "weighted_mean": 0.87,
    "min_dimension_score": 0.82
  }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RUBRIC_NOT_FOUND | no | Unknown or revoked `rubric_id` |
| TRAJECTORY_INVALID | no | Steps missing required fields or exceed limits |
| SCORING_TIMEOUT | yes | Model or rules engine exceeded deadline |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only.
