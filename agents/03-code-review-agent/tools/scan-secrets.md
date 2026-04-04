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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CONTENT_REF_INVALID | no | Opaque handle not found or expired |
| SCAN_ENGINE_ERROR | yes | Secret scanner backend failure |
| PAYLOAD_TOO_LARGE | no | Blob exceeds scanner limits |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only analysis.
