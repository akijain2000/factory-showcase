# Tool: `read_current_prompt`

## Purpose

Fetch the **authoritative** current prompt record for a `prompt_id`, including version metadata and integrity hash.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["prompt_id"],
  "properties": {
    "prompt_id": { "type": "string", "maxLength": 128 },
    "namespace": { "type": "string", "maxLength": 128, "default": "default" },
    "include_inactive": { "type": "boolean", "default": false }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "prompt_id": "inner/task-router",
  "version": "2026.04.03-11",
  "content": "… full prompt text …",
  "content_hash": "sha256:2b3c…",
  "tags": ["production", "pii_safe_template"],
  "updated_at": "2026-04-03T18:22:01Z"
}
```

## Side effects

Read-only against `PROMPT_REGISTRY_URI`. May emit audit read event. **Never** logs full `content` at INFO in production unless explicitly enabled.
