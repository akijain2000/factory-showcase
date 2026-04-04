# Tool: `detect_injection`

## Purpose

Heuristic and model-assisted detection of **prompt injection**, tool exfiltration attempts, jailbreak patterns, and delimiter abuse; returns severity and recommended action.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["text"],
  "properties": {
    "text": { "type": "string", "maxLength": 1000000 },
    "context": {
      "type": "object",
      "properties": {
        "channel": {
          "type": "string",
          "enum": ["web", "api", "email", "ticket", "unknown"]
        },
        "prior_fingerprint": { "type": "string" }
      }
    },
    "mode": {
      "type": "string",
      "enum": ["fast_rules", "hybrid", "full"],
      "default": "hybrid"
    },
    "detection_request_id": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "verdict": "suspicious",
  "severity": "medium",
  "action": "warn",
  "signals": [
    { "name": "delimiter_flood", "score": 0.62 },
    { "name": "tool_override_phrase", "score": 0.41 }
  ],
  "explanation_ref": "sec_expl_9c2"
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| MODEL_UNAVAILABLE | yes | Hybrid or full model path unavailable |
| TEXT_TOO_LARGE | no | `text` exceeds `maxLength` |
| RULE_ENGINE_ERROR | yes | Fast rules path failed |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s (`full` mode may use full budget)
- Rate limit: 200 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `detection_request_id` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 3600s

## Side effects

- Logs **signal summary** (not raw text) to security analytics when severity ≥ low.
- `action: block` may increment per-tenant rate limits.
