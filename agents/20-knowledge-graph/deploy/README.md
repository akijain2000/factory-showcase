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

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `GRAPH_DB_CREDENTIALS` | `GRAPH_STORE_REF` (TLS + user/pass or IAM) |
| `EMBED_INDEX_CREDENTIALS` | `GRAPH_EMBED_INDEX_REF` |
| `MODEL_API_KEY` | Extraction and reasoning `MODEL_API_ENDPOINT` |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Graph agent API | 500m | 4 | 1Gi | 4Gi |

Heavy extraction batches and large subgraph serialization benefit from higher memory; set `GRAPH_QUERY_TIMEOUT_MS` to cap tail latency.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when graph ping + embedding index ping + motif allowlist loaded |

Readiness should fail closed if allowlist bundle fails signature or version check in regulated deployments.
