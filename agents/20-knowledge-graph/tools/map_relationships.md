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
    },
    "edge_batch_idempotency_key": { "type": "string", "maxLength": 128 }
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

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| DOCUMENT_NOT_FOUND | no | Unknown `document_ref` |
| UPSERT_FAILED | yes | Graph store write error |
| DEDUP_CONFLICT | no | Edge collides with existing truthy assertion |
| THRESHOLD_POLICY | no | All candidates rejected by confidence rules |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `edge_batch_idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

- Writes **reviewable edges** to graph store or quarantine queue depending on confidence policy.
- May trigger **deduplication** against existing edges with same endpoints + predicate.
