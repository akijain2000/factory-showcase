# Tool: `retrieve_document`

## Purpose

Retrieve relevant chunks from the configured document index (vector + metadata filter).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["query"],
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "top_k": { "type": "integer", "minimum": 1, "maximum": 32, "default": 8 },
    "filters": {
      "type": "object",
      "additionalProperties": { "type": "string" },
      "description": "Metadata filters, e.g. {\"project_id\": \"payments\"}"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "chunks": [
    {
      "doc_id": "doc-123",
      "chunk_id": "doc-123#4",
      "text": "...",
      "score": 0.82,
      "metadata": { "title": "Onboarding Runbook", "section": "3.2" }
    }
  ]
}
```

## Side effects

Read-only against index.

## Auth

Service credentials via environment; never passed in prompt.
