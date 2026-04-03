# Tool: `downgrade_model`

## Purpose

Select a **lower-cost** alternative to the current routing choice while bounding acceptable quality loss.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["from_model", "reason"],
  "properties": {
    "from_model": { "type": "string", "maxLength": 128 },
    "reason": {
      "type": "string",
      "enum": [
        "BUDGET_PRESSURE",
        "CIRCUIT_BREAKER_WARN",
        "LATENCY_SLO_TIGHTEN",
        "OPERATOR_OVERRIDE"
      ]
    },
    "max_relative_quality_loss": {
      "type": "number",
      "minimum": 0,
      "maximum": 0.5,
      "default": 0.2
    },
    "task_class": {
      "type": "string",
      "maxLength": 64
    },
    "request_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "to_model": "text-econ-8k",
  "from_model": "text-capable-32k",
  "expected_savings_pct": 62,
  "quality_loss_estimate": 0.08
}
```

## Side effects

Logs structured downgrade event for FinOps review. May register **sticky downgrade** for burst windows if policy enables burst mode. Does not automatically revert until `route_to_model` is called again without sticky flag.
