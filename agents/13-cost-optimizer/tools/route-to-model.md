# Tool: `route_to_model`

## Purpose

Select a **model tier** and concrete **model id** from `MODEL_ROUTE_TABLE_REF` given task class, SLO, and quality band.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["task_class", "latency_slo_ms", "quality_band"],
  "properties": {
    "task_class": {
      "type": "string",
      "enum": [
        "classification",
        "summarization",
        "codegen",
        "tool_use_heavy",
        "general",
        "vision",
        "embedding"
      ]
    },
    "latency_slo_ms": { "type": "integer", "minimum": 50, "maximum": 600000 },
    "quality_band": {
      "type": "string",
      "enum": ["economy", "standard", "high"]
    },
    "region": { "type": "string", "maxLength": 32 },
    "budget_hint_usd": { "type": "number", "minimum": 0 },
    "request_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "tier": "fast",
  "model_id": "text-fast-8k",
  "router_reason": "classification_with_tight_slo",
  "estimated_usd_ceiling": 0.0042
}
```

## Side effects

Writes a **routing decision** row to the audit stream (no prompt body). May increment shadow-traffic counters if canary routing is enabled. Does not invoke `MODEL_API_ENDPOINT` by itself.
