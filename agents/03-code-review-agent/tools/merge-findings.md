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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| FINDING_SCHEMA_INVALID | no | Finding object missing required fields |
| MERGE_LIMIT_EXCEEDED | no | Input set too large for single merge |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

None.
