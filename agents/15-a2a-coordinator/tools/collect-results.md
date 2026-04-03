# Tool: `collect_results`

## Purpose

Gather **terminal or partial** outcomes for delegated tasks, normalize statuses, and detect **conflicts** when assertions disagree.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["task_handles"],
  "properties": {
    "task_handles": {
      "type": "array",
      "items": { "type": "string", "maxLength": 128 },
      "maxItems": 100
    },
    "wait_policy": {
      "type": "string",
      "enum": ["all_terminal", "first_success", "partial_ok"],
      "default": "all_terminal"
    },
    "per_handle_timeout_ms": { "type": "integer", "minimum": 100, "maximum": 600000, "default": 60000 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "results": [
    {
      "handle": "tsk_9pQm01",
      "state": "succeeded",
      "output_ref": "artifact://a2a/tsk_9pQm01/out.json",
      "confidence": 0.86
    }
  ],
  "conflicts": true,
  "conflict_set_id": "cfl_7nQs",
  "summary": "Two agents disagree on root cause classification."
}
```

## Side effects

May pull artifacts via signed URLs; writes **collection audit** with handle states. Marks hung tasks `timed_out` and frees waiter resources. Does not mutate peer agent state.
