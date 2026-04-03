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

## Side effects

Spawns or schedules sub-agent run (implementation-defined).

## Errors

`UNKNOWN_TARGET`, `SCOPE_EMPTY`, `HANDOFF_LIMIT`.
