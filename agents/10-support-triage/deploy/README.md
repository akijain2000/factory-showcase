# Deploy: Support Triage Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| CRM / ticketing API credentials | yes | `route_ticket`, `generate_response`, `escalate_to_human` |
| KB search endpoint + auth | yes* | *If `search_kb` is remote |
| `MODEL_API_KEY` | yes* | *Unless on-prem |

Log every `route_ticket` with ticket id and model version (see main README Governance).

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: CRM and KB reachability (read-only ping).

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 0.5–1 core |
| Memory | 512 MiB – 1 GiB |
| Tool timeout | 45s default |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# CRM API keys, KB credentials, MODEL_API_KEY

CMD ["python", "-c", "print('Wire helpdesk client; see src/agent.py')"]
```

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| CRM OAuth / API token | Ticket reads and updates |
| KB / vector index key | Grounded answers |
| `MODEL_API_KEY` | Classification and drafting |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 0.5–1 vCPU |
| Memory | 512 MiB – 1 GiB |
| Egress | Allowlist CRM + KB + LLM only |

## Health check configuration

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
```

## Operational notes

- Redact payment data and government IDs before model calls where regulations require it.
- Gate `generate_response` behind human approval in regulated industries.
