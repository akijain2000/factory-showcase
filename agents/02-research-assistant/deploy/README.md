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
