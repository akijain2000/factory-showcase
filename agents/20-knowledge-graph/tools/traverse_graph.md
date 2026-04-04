# Tool: `traverse_graph`

## Purpose

Traverses the knowledge graph from a start node up to `max_depth`, optionally filtering by relationship types. Returns an induced subgraph (nodes and edges) suitable for context expansion, path finding prep, or visualization.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "start_node_id": {
      "type": "string",
      "description": "Graph-local identifier of the seed entity.",
      "minLength": 1
    },
    "max_depth": {
      "type": "integer",
      "description": "Maximum hop distance from the start node.",
      "minimum": 0,
      "maximum": 32
    },
    "relationship_types": {
      "type": "array",
      "description": "If non-empty, only follow edges whose type is in this list.",
      "items": { "type": "string", "minLength": 1 }
    }
  },
  "required": ["start_node_id", "max_depth"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "subgraph": {
    "nodes": [
      {
        "id": "ent_acme",
        "label": "Organization",
        "properties": { "name": "Acme Corp" }
      },
      {
        "id": "ent_widget",
        "label": "Product",
        "properties": { "sku": "W-100" }
      }
    ],
    "edges": [
      {
        "id": "rel_1",
        "source": "ent_acme",
        "target": "ent_widget",
        "type": "PRODUCES",
        "properties": { "since": "2020" }
      }
    ],
    "meta": {
      "start_node_id": "ent_acme",
      "max_depth_requested": 2,
      "depth_reached": 1,
      "truncated": false
    }
  }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| NODE_NOT_FOUND | no | Unknown `start_node_id` |
| DEPTH_EXCEEDED | no | Traversal stopped by policy before `max_depth` |
| GRAPH_TIMEOUT | yes | Graph cluster query deadline exceeded |
| RESULT_TOO_LARGE | no | Induced subgraph exceeded materialization cap |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 90s
- Rate limit: 100 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 500 nodes / 2000 edges (implementation-defined split)
- Cursor-based: returns `next_cursor` in response when `subgraph.meta.truncated` is true
- Max results per call: 5000 total elements

## Side effects

Read-only.
