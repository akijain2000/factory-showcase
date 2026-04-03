# Tool: `run_evaluation`

## Purpose

Execute the pinned evaluation suite against a **prompt candidate** in an isolated runner, producing scored artifacts.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["suite_version", "prompt_candidate_id"],
  "properties": {
    "suite_version": { "type": "string", "maxLength": 64 },
    "prompt_candidate_id": { "type": "string", "maxLength": 128 },
    "random_seed": { "type": "integer" },
    "max_parallel": { "type": "integer", "minimum": 1, "maximum": 64, "default": 4 },
    "model_tier": {
      "type": "string",
      "description": "Logical tier for runner, not raw credentials",
      "maxLength": 64
    },
    "artifact_store_prefix": { "type": "string", "maxLength": 256 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "run_id": "eval_run_7nQs",
  "suite_version": "bench-2026.04.01",
  "summary": {
    "tasks_total": 240,
    "tasks_failed": 3,
    "primary_score_mean": 0.812
  },
  "artifact_uris": ["artifact://eval-artifacts/eval_run_7nQs/summary.json"]
}
```

## Side effects

Spends compute budget; writes artifacts to object store; records row in `METRICS_STORE_URI` with **run_id**. Uses `MODEL_API_ENDPOINT` indirectly through runner configuration—credentials remain outside prompts.
