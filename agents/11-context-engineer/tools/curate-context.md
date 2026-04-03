# Tool: `curate_context`

## Purpose

Rank, deduplicate, and structure raw artifacts (logs, files, messages) into a **bounded curated bundle** aligned with a stated objective. Produces stable `source_ref` identifiers for every retained chunk.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["objective", "raw_artifacts"],
  "properties": {
    "objective": {
      "type": "string",
      "maxLength": 8000,
      "description": "What the downstream model must accomplish with this context."
    },
    "raw_artifacts": {
      "type": "array",
      "maxItems": 500,
      "items": {
        "type": "object",
        "required": ["source_ref", "content", "kind"],
        "additionalProperties": false,
        "properties": {
          "source_ref": { "type": "string", "maxLength": 512 },
          "content": { "type": "string", "maxLength": 500000 },
          "kind": {
            "type": "string",
            "enum": ["message", "log", "file_excerpt", "metric", "ticket", "other"]
          },
          "timestamp": { "type": "string", "format": "date-time" },
          "priority_hint": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "max_items": { "type": "integer", "minimum": 1, "maximum": 256, "default": 64 },
    "redact_secrets": { "type": "boolean", "default": true }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "bundle_id": "ctx_bnd_01HZX8QVK9",
  "items": [
    {
      "rank": 1,
      "source_ref": "ticket:4821#comment-3",
      "excerpt": "…",
      "retention_reason": "blocking_error_stacktrace"
    }
  ],
  "dropped_count": 12,
  "estimated_tokens": 8420
}
```

## Side effects

Persists the bundle to `CONTEXT_STORE_URI` (or equivalent), emits an audit event with `bundle_id`, objective hash, and item count. **No** external network calls beyond the configured store. When `redact_secrets` is true, applies host redaction rules and logs redaction counts only (not raw matches).
