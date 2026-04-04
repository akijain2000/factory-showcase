# Tool: `reason_over_path`

## Purpose

Finds and reasons over connecting structure between two entities in the knowledge graph, then answers a natural-language question using that path as grounding. Returns a concise answer plus the supporting node/edge sequence for auditability.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "source_id": {
      "type": "string",
      "description": "Start entity id in the graph.",
      "minLength": 1
    },
    "target_id": {
      "type": "string",
      "description": "End entity id in the graph.",
      "minLength": 1
    },
    "question": {
      "type": "string",
      "description": "Question to answer using the path as evidence.",
      "minLength": 1
    }
  },
  "required": ["source_id", "target_id", "question"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "answer": "Acme Corp produces the Widget Pro line through its manufacturing subsidiary.",
  "supporting_path": {
    "nodes": [
      { "id": "ent_acme", "label": "Organization" },
      { "id": "ent_sub_manu", "label": "Subsidiary" },
      { "id": "ent_widget_pro", "label": "ProductLine" }
    ],
    "edges": [
      { "type": "OWNS", "source": "ent_acme", "target": "ent_sub_manu" },
      { "type": "MANUFACTURES", "source": "ent_sub_manu", "target": "ent_widget_pro" }
    ]
  },
  "confidence": 0.78,
  "notes": "Shortest path length 2; alternative paths exist via distribution partners."
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| ENTITY_NOT_FOUND | no | `source_id` or `target_id` not in graph |
| PATH_NOT_FOUND | no | No connecting path within policy limits |
| REASONING_TIMEOUT | yes | Path search or LLM grounding exceeded deadline |
| GRAPH_UNAVAILABLE | yes | Graph backend error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 120s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only.
