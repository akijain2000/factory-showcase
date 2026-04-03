# Tool: `scan_secrets` (security_reviewer)

## Purpose

Scan text for high-confidence secret patterns (API keys, tokens, private keys).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["content_ref"],
  "properties": {
    "content_ref": {
      "type": "string",
      "description": "Opaque handle to diff or file blob provided by runtime"
    },
    "strictness": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "default": "high"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "findings": [
    {
      "id": "sec-001",
      "severity": "CRITICAL",
      "path": "src/config.ts",
      "line": 12,
      "rule": "generic-api-key",
      "evidence": "REDACTED"
    }
  ]
}
```

## Side effects

Read-only analysis.
