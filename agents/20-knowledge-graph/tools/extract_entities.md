# Tool: `extract_entities`

## Purpose

Detect and normalize **named entities** and concepts from text: types, surface forms, canonical ids, confidence, and document provenance for graph upsert.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["document_ref", "text"],
  "properties": {
    "document_ref": { "type": "string", "maxLength": 512 },
    "text": { "type": "string", "maxLength": 200000 },
    "language": { "type": "string", "maxLength": 16, "default": "und" },
    "entity_types": {
      "type": "array",
      "items": { "type": "string", "maxLength": 64 },
      "maxItems": 64
    },
    "linking_mode": {
      "type": "string",
      "enum": ["none", "fuzzy", "embeddings"],
      "default": "embeddings"
    },
    "extraction_idempotency_key": { "type": "string", "maxLength": 128 }
  }
}
```

## Return shape

```json
{
  "entities": [
    {
      "id": "ent_acme_corp",
      "label": "Acme Corp",
      "type": "Organization",
      "confidence": 0.91,
      "mentions": [{ "start": 12, "end": 21, "text": "Acme Corp" }]
    }
  ],
  "warnings": []
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| DOCUMENT_TOO_LARGE | no | `text` exceeds deployment limit |
| EXTRACTION_MODEL_ERROR | yes | NER/linking backend failure |
| LINKING_TIMEOUT | yes | Embedding or fuzzy match deadline exceeded |
| STAGING_WRITE_FAILED | yes | Staging store error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 180s
- Rate limit: 50 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `extraction_idempotency_key` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 86400s

## Side effects

- May upsert **candidate entities** into a staging table keyed by `document_ref`.
- Embedding calls may incur **cost metering** per tenant.
