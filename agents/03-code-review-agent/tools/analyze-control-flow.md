# Tool: `analyze_control_flow` (logic_reviewer)

## Purpose

Summarize control flow and flag likely bug patterns: missing error handling, early returns that skip cleanup, obvious race windows (heuristic).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["content_ref", "language"],
  "properties": {
    "content_ref": { "type": "string" },
    "language": { "type": "string" },
    "focus": { "type": "string", "description": "Optional symbol or region hint" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "notes": [
    "Async task spawned without cancellation on timeout (heuristic)."
  ],
  "findings": [
    {
      "id": "log-003",
      "severity": "MEDIUM",
      "path": "worker/jobs.py",
      "line": 88,
      "message": "Resource acquired; no finally/ctx manager on error path"
    }
  ]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CONTENT_REF_INVALID | no | Opaque handle not found or expired |
| LANGUAGE_UNSUPPORTED | no | Analyzer does not support `language` |
| ANALYSIS_TIMEOUT | yes | Static analysis exceeded deadline |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only / static analysis.
