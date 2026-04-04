# Deploy: Research Assistant Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `RESEARCH_MEMORY_STORE` | yes | Memory backend URI |
| `RESEARCH_DOC_INDEX` | yes | Retrieval collection / endpoint id |
| `RESEARCH_MAX_WEB_RESULTS` | no | Default cap (e.g. `5`) |
| Search provider keys | yes | e.g. `BING_SEARCH_KEY` or vendor equivalent |

Secrets via vault; never in `system-prompt.md`.

## Health check

- `GET /healthz`: process up, can reach doc index (lightweight ping), memory store reachable.
- `GET /readyz`: index schema version matches expected.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Memory | 512 MiB – 1 GiB |
| CPU | 1–2 cores |
| Retrieval timeout | 5–15s |
| Web search timeout | 10–20s |
| Max tool calls per turn | 12 |

## Observability

Log trace id per user turn; record tool latency and provider error codes (no raw document text in logs).

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# RESEARCH_MEMORY_STORE, RESEARCH_DOC_INDEX, search provider keys, MODEL_API_KEY — from secrets at runtime

CMD ["python", "-c", "print('Wire HTTP + retrieval clients; see src/agent.py')"]
```

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| `RESEARCH_MEMORY_STORE` | Durable memory backend |
| `RESEARCH_DOC_INDEX` | Vector / search collection |
| Search API key (e.g. vendor-specific) | `web_search` tool |
| `MODEL_API_KEY` | LLM provider |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 1–2 vCPU |
| Memory | 512 MiB – 1 GiB |
| Egress | Allowlist search + index endpoints only |

## Health check configuration

- `GET /healthz`: process up, doc index ping OK, memory store reachable.
- `GET /readyz`: optional schema/version match for index.

```yaml
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
  periodSeconds: 15
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  periodSeconds: 30
```
