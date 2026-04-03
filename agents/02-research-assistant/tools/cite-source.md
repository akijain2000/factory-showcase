# Tool: `cite_source`

## Purpose

Normalize and validate citation records so the final answer uses consistent metadata.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["kind", "ref"],
  "properties": {
    "kind": { "type": "string", "enum": ["web", "corpus"] },
    "ref": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string" },
        "url": { "type": "string", "format": "uri" },
        "title": { "type": "string" },
        "accessed_at": { "type": "string", "format": "date-time" },
        "doc_id": { "type": "string" },
        "chunk_id": { "type": "string" }
      }
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "citation": {
    "marker": "[1]",
    "id": "cit-1",
    "display": "Onboarding Runbook (doc-123), §3.2"
  }
}
```

## Side effects

None.
