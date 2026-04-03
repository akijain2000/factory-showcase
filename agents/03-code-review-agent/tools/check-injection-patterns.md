# Tool: `check_injection_patterns` (security_reviewer)

## Purpose

Heuristic scan for SQL/string concatenation injection risks and unsafe deserialization call sites.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["content_ref", "language"],
  "properties": {
    "content_ref": { "type": "string" },
    "language": { "type": "string", "enum": ["python", "typescript", "javascript", "go", "java", "other"] }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "findings": [
    {
      "id": "sec-014",
      "severity": "HIGH",
      "path": "api/query.py",
      "line": 44,
      "rule": "sql-string-concat",
      "message": "User input concatenated into SQL string"
    }
  ]
}
```

## Side effects

Read-only.
