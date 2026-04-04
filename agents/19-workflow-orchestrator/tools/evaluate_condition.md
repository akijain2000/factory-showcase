# Tool: `evaluate_condition`

## Purpose

Evaluate a **named branching expression** against structured `facts` produced by prior steps; returns a discrete decision for edge selection.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["expression_ref", "facts"],
  "properties": {
    "expression_ref": {
      "type": "string",
      "description": "Registry key for approved expression bundle (CEL/Rego/etc.)."
    },
    "facts": {
      "type": "object",
      "description": "JSON-serializable fact map; must not include secrets."
    },
    "expected_type": {
      "type": "string",
      "enum": ["boolean", "enum", "number"],
      "default": "boolean"
    },
    "enum_labels": {
      "type": "array",
      "items": { "type": "string" },
      "maxItems": 32
    },
    "condition_eval_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "value": true,
  "branch": "approve_path",
  "trace": [{ "rule": "amount_within_limit", "result": true }],
  "duration_ms": 3
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| EXPRESSION_NOT_FOUND | no | Unknown `expression_ref` |
| FACTS_INVALID | no | `facts` failed schema or size checks |
| EVALUATION_ERROR | no | Expression runtime error |
| COMPILE_CACHE_ERROR | yes | Expression compile cache unavailable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 300 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `condition_eval_id` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 3600s

## Side effects

- Logs **expression_ref** + outcome to workflow audit (facts redacted).
- Caches compiled expression where supported to reduce latency.
