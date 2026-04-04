# Tool: `query_subgraph`

## Purpose

Retrieve a **pattern-shaped subgraph** (e.g., star, path, small motif) matching declarative constraints for downstream reasoning.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["pattern", "bindings"],
  "properties": {
    "pattern": {
      "type": "string",
      "enum": ["star", "path", "motif_cypher_ref", "typed_neighborhood"]
    },
    "bindings": {
      "type": "object",
      "description": "Anchor ids and parameters; no raw query injection."
    },
    "motif_ref": {
      "type": "string",
      "description": "Required when pattern is motif_cypher_ref; server-side allowlisted."
    },
    "limit": { "type": "integer", "minimum": 1, "maximum": 2000, "default": 200 },
    "include_evidence": { "type": "boolean", "default": true }
  }
}
```

## Return shape

```json
{
  "matches": [
    {
      "nodes": [],
      "edges": [],
      "score": 0.88
    }
  ],
  "stats": { "match_count": 3, "pruned": false }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| PATTERN_INVALID | no | `pattern` incompatible with `bindings` |
| MOTIF_NOT_ALLOWLISTED | no | `motif_ref` not registered |
| QUERY_TIMEOUT | yes | Graph query exceeded deadline |
| BINDING_ERROR | no | Invalid or out-of-scope anchor in `bindings` |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 80 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 200 (same as default `limit`)
- Cursor-based: returns `next_cursor` in response
- Max results per call: 2000

## Side effects

- Executes **compiled** server-side queries only; rejects ad-hoc strings not in allowlist.
- May warm **page cache** on the graph cluster.
