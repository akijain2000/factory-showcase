# Knowledge Graph Agent

An **entity–relation** reasoning agent that extracts structured concepts from documents, maps **typed relationships**, persists them in a graph store, runs **bounded traversals**, and answers questions via **subgraph retrieval** plus path-level reasoning.

## Audience

Data teams and research copilots that need explainable answers grounded in an evolving knowledge graph rather than flat chunk retrieval alone.

## Quickstart

1. Load `system-prompt.md`.
2. Wire `tools/` to your NLP pipeline, graph database, and embedding index.
3. Configure `GRAPH_STORE_REF` per `deploy/README.md`.
4. Validate with `tests/extract-traverse-reason-path.md`.

## Configuration

| Variable | Description |
|----------|-------------|
| `GRAPH_STORE_REF` | Graph DB connection reference (vault) |
| `GRAPH_EMBED_INDEX_REF` | Vector index for entity linking |
| `MODEL_API_ENDPOINT` | Model for extraction and reasoning summaries |

## Architecture

```
 +----------------+
 | Document input |
 +--------+-------+
          |
          v
 +-------------------+
 | Entity extractor  |
 +---------+---------+
           |
           v
 +-------------------+
 | Relationship      |
 | mapper            |
 +---------+---------+
           |
           v
 +-------------------+
 | Graph store       |
 +---------+---------+
           |
     +-----+-----+
     |           |
     v           v
+----------------+   +-------------------+
| Query engine   |   | Path reasoner     |
| (subgraph)     |   | (multi-hop logic) |
+----------------+   +-------------------+
           \           /
            v         v
         +----------------+
         | Final answer   |
         +----------------+
```

## Design notes

- Entities carry **provenance** (doc id, offsets) for auditability.
- Traversals are **budgeted** by hop count and edge types to contain cost.
- Reasoning outputs label **inference vs observed** edges explicitly.

## Testing

See `tests/extract-traverse-reason-path.md`.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
