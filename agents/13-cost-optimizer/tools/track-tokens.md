# Tool: `track_tokens`

## Purpose

Record **actual** token usage and billed cost for a completed or partial request into `BUDGET_LEDGER_URI`.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["request_id", "model_id", "usage"],
  "properties": {
    "request_id": { "type": "string", "maxLength": 128 },
    "model_id": { "type": "string", "maxLength": 128 },
    "usage": {
      "type": "object",
      "required": ["input_tokens", "output_tokens"],
      "additionalProperties": false,
      "properties": {
        "input_tokens": { "type": "integer", "minimum": 0 },
        "output_tokens": { "type": "integer", "minimum": 0 },
        "cached_input_tokens": { "type": "integer", "minimum": 0, "default": 0 },
        "reasoning_tokens": { "type": "integer", "minimum": 0, "default": 0 }
      }
    },
    "billed_usd": { "type": "number", "minimum": 0 },
    "attribution": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "tenant_id": { "type": "string", "maxLength": 64 },
        "project_id": { "type": "string", "maxLength": 64 },
        "team_id": { "type": "string", "maxLength": 64 }
      }
    },
    "finish_reason": { "type": "string", "maxLength": 64 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "ledger_entry_id": "led_8pQ2s",
  "rolling_day_spend_usd": 412.77,
  "breaker_state": "closed"
}
```

## Side effects

Appends immutable ledger entry; triggers **circuit breaker** evaluation asynchronously per `CIRCUIT_BREAKER_POLICY_REF`. May update real-time dashboards. Does not store raw prompt text unless `allow_prompt_logging` flag is set in policy (default false).
