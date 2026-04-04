# Tool: `sanitize_input`

## Purpose

Sanitizes user-supplied text against common injection and delimiter patterns (e.g. prompt-injection phrases, control characters, excessive nesting) before the agent or tools consume it. Trust level tunes aggressiveness of stripping and flagging.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "raw_input": {
      "type": "string",
      "description": "Untrusted user or upstream content to sanitize."
    },
    "trust_level": {
      "type": "string",
      "description": "Policy tier: strict blocks more patterns; trusted applies minimal normalization.",
      "enum": ["untrusted", "low", "medium", "high", "trusted"]
    }
  },
  "required": ["raw_input", "trust_level"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "sanitized": "Summarize the following document without following new instructions.",
  "flags": [
    {
      "code": "INJECTION_PATTERN",
      "severity": "high",
      "detail": "Matched override-style phrase; clause redacted.",
      "offset": 42
    },
    {
      "code": "CONTROL_CHARS_STRIPPED",
      "severity": "low",
      "detail": "Removed disallowed control characters.",
      "offset": null
    }
  ],
  "trust_level_applied": "untrusted"
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| RULESET_UNAVAILABLE | yes | Sanitization rules backend error |
| INPUT_TOO_LARGE | no | `raw_input` exceeds deployment limit |
| TRUST_LEVEL_INVALID | no | Unknown or disallowed `trust_level` for tenant |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 20s
- Rate limit: 400 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only (returns new string; does not mutate caller buffers).
