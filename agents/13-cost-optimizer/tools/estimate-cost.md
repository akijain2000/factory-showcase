# Tool: `estimate_cost`

## Purpose

Preflight **USD** and **token envelope** estimates for candidate models before invoking the provider.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["task_class", "input_tokens_est", "output_tokens_est"],
  "properties": {
    "task_class": { "type": "string", "maxLength": 64 },
    "input_tokens_est": { "type": "integer", "minimum": 0 },
    "output_tokens_est": { "type": "integer", "minimum": 0 },
    "candidate_models": {
      "type": "array",
      "items": { "type": "string", "maxLength": 128 },
      "maxItems": 8
    },
    "pricing_table_ref": {
      "type": "string",
      "description": "Optional override pointer",
      "maxLength": 256
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "estimates": [
    {
      "model_id": "text-fast-8k",
      "usd": 0.0011,
      "assumptions": ["no_cached_prefix"]
    },
    {
      "model_id": "text-capable-32k",
      "usd": 0.0096,
      "assumptions": ["no_cached_prefix"]
    }
  ],
  "min_usd": 0.0011,
  "max_usd": 0.0096
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PRICING_SNAPSHOT_STALE | yes | Pricing table version mismatch |
| MODEL_UNKNOWN | no | Candidate model id not in table |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 400 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only against pricing snapshots; may cache results keyed by `(pricing_snapshot_id, token_tuple_hash)` with short TTL. No ledger write.
