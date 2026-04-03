# Tool: `lint_style_conventions` (style_reviewer)

## Purpose

Run configured style rules (naming, import order, formatting drift vs project guide).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["path"],
  "properties": {
    "path": { "type": "string", "description": "File path in repo" },
    "ruleset": { "type": "string", "description": "e.g. ruff, eslint, internal" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "violations": [
    { "line": 3, "code": "N801", "message": "Class names should use CapWords" }
  ]
}
```

## Side effects

May invoke local linter subprocess (sandboxed).
