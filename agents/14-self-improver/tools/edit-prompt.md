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

## Side effects

Writes candidate record; triggers optional static **lint** (forbidden phrases, length). On `parent_hash` mismatch, returns `VERSION_CONFLICT` without creating a candidate.
