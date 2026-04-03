# Deploy: Knowledge Graph Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `GRAPH_STORE_REF` | yes | Graph database credentials reference |
| `GRAPH_EMBED_INDEX_REF` | yes | Vector index for entity linking |
| `MODEL_API_ENDPOINT` | yes | Model for extraction/reasoning phrasing |
| `GRAPH_QUERY_TIMEOUT_MS` | optional | Server-side cap for traversals and motifs |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: graph store ping; embedding index ping; motif allowlist bundle loaded.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| `traverse_graph.limit` | 500–2000 depending on cluster |
| `max_hops` | ≤ 8; lower for dense graphs |
| Extraction batch size | 50–200 KB text per call |

## Operational notes

- **Provenance:** store `document_ref` on every entity and edge for GDPR delete workflows.
- **Deduplication:** reconcile entities with periodic offline clustering jobs; surface merge candidates to reviewers.
- **Safety:** disallow free-text graph query injection—only `motif_ref` and compiled patterns.
