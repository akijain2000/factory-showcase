# Tool: `validate_output`

## Purpose

Validates agent-generated output against a named policy before it is returned to the user or downstream systems. Can enforce PII redaction, secret patterns, length bounds, and disallowed content lists; returns a validation verdict and optionally redacted text.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "output": {
      "type": "string",
      "description": "Candidate assistant or tool output to validate."
    },
    "policy_id": {
      "type": "string",
      "description": "Identifier of the validation policy bundle (ruleset) to apply.",
      "minLength": 1
    }
  },
  "required": ["output", "policy_id"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "validation": {
    "ok": false,
    "policy_id": "policy_customer_facing_v2",
    "violations": [
      {
        "rule": "no_raw_email",
        "severity": "block",
        "message": "Email-like pattern detected.",
        "span": { "start": 120, "end": 142 }
      }
    ]
  },
  "redacted_output": "Contact us at [REDACTED] for more details.",
  "applied_redactions": 1
}
```

## Side effects

Read-only (output is not written to durable storage by this tool; callers may persist `redacted_output`).
