# Tool: `edit_prompt`

## Purpose

Create a **candidate** prompt revision from a parent hash using a unified diff or structured operations; does not promote to production.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["prompt_id", "parent_hash", "diff_unified", "rationale"],
  "properties": {
    "prompt_id": { "type": "string", "maxLength": 128 },
    "namespace": { "type": "string", "maxLength": 128, "default": "default" },
    "parent_hash": { "type": "string", "maxLength": 200 },
    "diff_unified": { "type": "string", "maxLength": 500000 },
    "rationale": { "type": "string", "maxLength": 8000 },
    "author": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "candidate_id": "prm_cand_9Lm2",
  "parent_hash": "sha256:2b3c…",
  "new_hash": "sha256:91af…",
  "validation": {
    "diff_parses": true,
    "safety_tags_preserved": true
  }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| VERSION_CONFLICT | no | `parent_hash` does not match registry |
| DIFF_REJECTED | no | Diff failed lint or safety checks |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 600s

## Side effects

Writes candidate record; triggers optional static **lint** (forbidden phrases, length). On `parent_hash` mismatch, returns `VERSION_CONFLICT` without creating a candidate.
