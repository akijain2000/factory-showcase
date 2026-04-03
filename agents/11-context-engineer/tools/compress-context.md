# Tool: `compress_context`

## Purpose

Loss-aware compression of an existing curated bundle to a target token budget while honoring **immutable** tags (safety, tool contracts, verbatim errors).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["bundle_id", "target_tokens"],
  "properties": {
    "bundle_id": { "type": "string", "maxLength": 128 },
    "target_tokens": { "type": "integer", "minimum": 512, "maximum": 2000000 },
    "preserve_tags": {
      "type": "array",
      "items": { "type": "string", "maxLength": 64 },
      "default": ["safety", "tool_contract", "error_trace"]
    },
    "strategy": {
      "type": "string",
      "enum": ["summarize_tail", "merge_similar", "hierarchical_outline", "auto"],
      "default": "auto"
    },
    "compression_model_hint": {
      "type": "string",
      "description": "Logical model tier label for summarization worker",
      "maxLength": 64
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "compressed_bundle_id": "ctx_bnd_01HZX8QW2A",
  "parent_bundle_id": "ctx_bnd_01HZX8QVK9",
  "estimated_tokens_before": 8420,
  "estimated_tokens_after": 5100,
  "removed_sections": ["verbose_success_log_lines_120_480"],
  "preserved_immutable_count": 4
}
```

## Side effects

Writes new bundle revision linked to parent; records compression provenance (strategy, token deltas). If infeasible to meet `target_tokens` without violating `preserve_tags`, returns `ok: false` with `error.code: COMPRESSION_INFEASIBLE` and does not mutate the original bundle.
