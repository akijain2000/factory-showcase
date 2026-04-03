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

## Side effects

- Executes **compiled** server-side queries only; rejects ad-hoc strings not in allowlist.
- May warm **page cache** on the graph cluster.
