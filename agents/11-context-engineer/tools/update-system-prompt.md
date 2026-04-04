# Tool: `update_system_prompt`

## Purpose

Create or promote a **versioned** system prompt revision under namespace policy. Supports **dry run** diff validation without activation.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["parent_version", "diff_unified", "change_rationale"],
  "properties": {
    "namespace": { "type": "string", "maxLength": 128 },
    "parent_version": { "type": "string", "maxLength": 64 },
    "diff_unified": { "type": "string", "maxLength": 500000 },
    "change_rationale": { "type": "string", "maxLength": 8000 },
    "dry_run": { "type": "boolean", "default": true },
    "review_ticket_id": { "type": "string", "maxLength": 128 },
    "expected_base_hash": {
      "type": "string",
      "description": "Optimistic concurrency token for parent content",
      "maxLength": 128
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "dry_run": true,
  "proposed_version": "2026.04.04-ctx-14",
  "validation": {
    "safety_constraints_preserved": true,
    "tool_sections_preserved": true,
    "diff_lines": 37
  },
  "promotion_blocked_reason": null
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| VERSION_CONFLICT | no | `expected_base_hash` mismatch with parent content |
| DIFF_REJECTED | no | Unified diff failed validation or policy checks |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 30 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `review_ticket_id` (optional field in arguments; pair with `parent_version` for dedupe)
- Safe to retry: yes when `dry_run` is true; promotion retries require matching `expected_base_hash`
- Duplicate detection window: 600s

## Side effects

When `dry_run` is **false** and review policy passes, registers new prompt version in `PROMPT_VERSION_NAMESPACE`, updates **routing** metadata for hosts that consume version pins, and writes an audit log entry (operator identity from host). On conflict with `expected_base_hash`, returns `VERSION_CONFLICT` and performs **no** promotion.
