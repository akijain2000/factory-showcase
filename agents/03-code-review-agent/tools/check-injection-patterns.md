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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CONTENT_REF_INVALID | no | Opaque handle not found or expired |
| PARSE_ERROR | no | Source could not be parsed for scan |
| SCAN_TIMEOUT | yes | Heuristic scan exceeded deadline |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only.
