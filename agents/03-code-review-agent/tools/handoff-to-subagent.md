# Tool: `handoff_to_subagent`

## Purpose

Supervisor-only: delegate a review slice to a specialized sub-agent with explicit scope and objective.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["target", "objective", "scope"],
  "properties": {
    "target": {
      "type": "string",
      "enum": ["security_reviewer", "style_reviewer", "logic_reviewer"]
    },
    "objective": { "type": "string", "maxLength": 2000 },
    "scope": {
      "type": "object",
      "required": ["paths"],
      "properties": {
        "paths": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
        "diff_hunk_ids": { "type": "array", "items": { "type": "string" } }
      }
    },
    "context": {
      "type": "object",
      "description": "Optional metadata: language, framework, threat model notes"
    },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Optional dedupe key; duplicate handoffs may still spawn distinct runs."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "handoff_id": "hnd-7f91",
  "target": "security_reviewer",
  "subagent_trace_id": "sub-abc"
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| UNKNOWN_TARGET | no | `target` not a registered sub-agent |
| SCOPE_EMPTY | no | `scope.paths` empty or invalid |
| HANDOFF_LIMIT | yes | Concurrency or depth limit reached |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 15s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: no
- Duplicate detection window: 60s

## Side effects

Spawns or schedules sub-agent run (implementation-defined).

## Errors

`UNKNOWN_TARGET`, `SCOPE_EMPTY`, `HANDOFF_LIMIT`.
