# Tool: `trace_aggregate`

## Purpose

Collects execution traces from concurrent tool calls into a unified timeline with branch IDs. Events from all branches are normalized, sorted (typically by timestamp), and correlated so operators and evaluators can inspect parallel work as one narrative.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "branch_ids": {
      "type": "array",
      "description": "Identifiers of execution branches whose traces should be merged.",
      "items": { "type": "string", "minLength": 1 },
      "minItems": 1
    },
    "include_metadata": {
      "type": "boolean",
      "description": "When true, include worker, tool name, and duration fields on each timeline entry.",
      "default": false
    }
  },
  "required": ["branch_ids"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "unified_trace": {
    "branches_included": ["branch-a", "branch-b"],
    "timeline": [
      {
        "ts": "2026-04-04T12:00:01.000Z",
        "branch_id": "branch-a",
        "event": "tool_start",
        "tool": "fetch",
        "metadata": { "worker": "w1", "duration_ms": null }
      },
      {
        "ts": "2026-04-04T12:00:01.050Z",
        "branch_id": "branch-b",
        "event": "tool_start",
        "tool": "summarize",
        "metadata": { "worker": "w2", "duration_ms": null }
      },
      {
        "ts": "2026-04-04T12:00:02.100Z",
        "branch_id": "branch-a",
        "event": "tool_end",
        "tool": "fetch",
        "metadata": { "worker": "w1", "duration_ms": 1100 }
      }
    ],
    "stats": {
      "event_count": 3,
      "branch_count": 2
    }
  }
}
```

## Side effects

Read-only.
