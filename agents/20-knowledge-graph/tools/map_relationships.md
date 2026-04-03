# Tool: `map_relationships`

## Purpose

Propose **typed edges** between entities with evidence spans, confidence, and temporal qualifiers when applicable.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["document_ref", "entity_ids", "candidates"],
  "properties": {
    "document_ref": { "type": "string" },
    "entity_ids": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 2,
      "maxItems": 200
    },
    "candidates": {
      "type": "array",
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["subject", "predicate", "object"],
        "properties": {
          "subject": { "type": "string" },
          "predicate": { "type": "string", "maxLength": 128 },
          "object": { "type": "string" },
          "evidence": { "type": "string", "maxLength": 4000 },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "valid_from": { "type": "string", "format": "date" },
          "valid_to": { "type": "string", "format": "date" }
        }
      }
    }
  }
}
```

## Return shape

```json
{
  "edges": [
    {
      "id": "e_4821",
      "subject": "ent_acme_corp",
      "predicate": "OWNS",
      "object": "ent_widget_line",
      "confidence": 0.74,
      "provenance": { "document_ref": "doc_9a", "span": { "start": 120, "end": 186 } }
    }
  ],
  "rejected": [{ "triple": "OWNS", "reason": "below_threshold" }]
}
```

## Side effects

- Writes **reviewable edges** to graph store or quarantine queue depending on confidence policy.
- May trigger **deduplication** against existing edges with same endpoints + predicate.
