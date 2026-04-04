# Deploy: Incident Responder Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| Observability credentials | yes | Metrics/logs APIs used by `check_health` / `query_logs` |
| Paging / ticketing API keys | yes* | *If `notify_oncall` / `create_incident` enabled |
| `INCIDENT_MAX_AUTONOMY` | no | Align with `autonomous_tool_budget` (default `12`) |
| `MODEL_API_KEY` | yes* | *Unless on-prem |

Default-deny destructive remediation in tool implementations; allowlist per environment.

## Health check

- `GET /healthz`: agent process up.
- `GET /readyz`: can reach read-only observability endpoints (no mutation).

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 1–2 cores |
| Memory | 512 MiB – 1 GiB |
| Tool timeout | 60s default; raise for heavy diagnostics |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# Observability tokens, paging keys, MODEL_API_KEY — from secrets manager

CMD ["python", "-c", "print('Wire on-call + telemetry clients; see src/agent.py')"]
```

Run in a restricted network segment; egress only to observability, ticketing, and LLM endpoints.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| Metrics/logs read tokens | Diagnostics |
| Pager / chat webhook | `notify_oncall` |
| Ticketing API | `create_incident` |
| `MODEL_API_KEY` | Triage LLM |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 1–2 vCPU |
| Memory | 512 MiB – 1 GiB |
| Rate limits | Respect vendor quotas for log queries |

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

- Scrub customer data from log excerpts before sending to third-party LLMs.
- Mirror high-severity incidents to humans regardless of agent success.
