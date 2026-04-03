# Tool: `generate_rubric`

## Purpose

Generates task-specific evaluation rubrics from a natural-language task description. Dimensions are tailored to what success means for that task (e.g. correctness, completeness, safety), so downstream scoring can grade agent trajectories consistently.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "task_description": {
      "type": "string",
      "description": "Description of the user-facing task or goal to evaluate against.",
      "minLength": 1
    },
    "num_dimensions": {
      "type": "integer",
      "description": "Number of rubric dimensions to produce.",
      "default": 5,
      "minimum": 1,
      "maximum": 20
    }
  },
  "required": ["task_description"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "rubric": {
    "rubric_id": "rubric_01HZX9K3",
    "task_summary": "Answer user questions using only approved documents.",
    "dimensions": [
      {
        "id": "dim_1",
        "name": "Factual grounding",
        "description": "Claims are supported by cited or retrievable sources.",
        "weight": 0.25,
        "scale": { "min": 0, "max": 1 }
      },
      {
        "id": "dim_2",
        "name": "Task completeness",
        "description": "All explicit sub-questions in the task are addressed.",
        "weight": 0.2,
        "scale": { "min": 0, "max": 1 }
      }
    ]
  }
}
```

## Side effects

Read-only (may persist rubric in backing store if your deployment enables caching; default spec assumes ephemeral generation only).
