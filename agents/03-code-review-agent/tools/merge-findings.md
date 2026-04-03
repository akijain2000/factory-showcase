# Tool: `merge_findings` (supervisor)

## Purpose

Normalize, deduplicate, and sort findings from sub-agents.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["findings"],
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "severity", "path", "message"],
        "properties": {
          "id": { "type": "string" },
          "severity": { "type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"] },
          "path": { "type": "string" },
          "line": { "type": "integer" },
          "message": { "type": "string" },
          "source_agent": { "type": "string" }
        }
      }
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "merged": ["... sorted ..."],
  "deduped_count": 2
}
```

## Side effects

None.
