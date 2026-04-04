# Tool: `reflect_on_output`

## Purpose

Produce a **structured post-mortem** of a model output against explicit success criteria: what worked, what failed, what to change in context or instructions next turn.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["task_objective", "model_output", "success_criteria"],
  "properties": {
    "task_objective": { "type": "string", "maxLength": 8000 },
    "model_output": { "type": "string", "maxLength": 500000 },
    "success_criteria": {
      "type": "array",
      "maxItems": 32,
      "items": { "type": "string", "maxLength": 2000 }
    },
    "tool_trace": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "ok"],
        "properties": {
          "name": { "type": "string" },
          "ok": { "type": "boolean" },
          "latency_ms": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "session_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "insights": [
    {
      "category": "missing_evidence",
      "severity": "high",
      "detail": "Answer assumed API behavior not present in curated bundle.",
      "suggested_action": "add_contract_excerpt"
    }
  ],
  "hypotheses": ["Model over-weighted stale summary vs. fresh error trace."],
  "next_turn_context_hints": ["Pin stacktrace chunk rank<=3"]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| REFLECTION_FAILED | yes | Internal reflection worker error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `session_id` (optional field in arguments; same session + content hash dedupes)
- Safe to retry: yes
- Duplicate detection window: 300s

## Side effects

Appends reflection record to session store keyed by `session_id`; may enqueue a low-priority **analytics** event (aggregated metrics only). Does not modify live system prompt.
