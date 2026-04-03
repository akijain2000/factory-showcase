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

## Side effects

When `dry_run` is **false** and review policy passes, registers new prompt version in `PROMPT_VERSION_NAMESPACE`, updates **routing** metadata for hosts that consume version pins, and writes an audit log entry (operator identity from host). On conflict with `expected_base_hash`, returns `VERSION_CONFLICT` and performs **no** promotion.
