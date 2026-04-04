# Deploy: Cost Optimizer Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `BUDGET_LEDGER_URI` | yes | Append-only usage and spend store |
| `MODEL_ROUTE_TABLE_REF` | yes | Routing matrix for tiers and model ids |
| `CIRCUIT_BREAKER_POLICY_REF` | yes | Thresholds, windows, webhook targets |
| `PRICING_TABLE_REF` | yes | Versioned per-million-token rates for `estimate_cost` |
| `MODEL_API_ENDPOINT` | optional | Agent’s own calls; credentials via secret manager |

## Health

- **/healthz:** process up.
- **/readyz:** pricing snapshot loaded; ledger writable; route table schema version compatible.

## Performance

| Concern | Guidance |
|---------|----------|
| Ledger hot spots | Shard by `tenant_id`; batch `track_tokens` for streaming chunks |
| estimate_cost cache | TTL 30–120s; invalidate on pricing snapshot change |
| Breaker evaluation | Async worker; avoid blocking request path |

## Security & compliance

- Store **hashed** or minimized attribution in logs; honor data residency for ledger region.
- Restrict `OPERATOR_OVERRIDE` downgrades to break-glass roles.
- Never embed provider secrets in this repo; mount via platform secret store at runtime.

## Observability

- Metrics: `route_decisions_total`, `downgrade_total`, `breaker_open_total`, `estimate_error_total`, `ledger_write_latency_ms`.
- Dashboards: spend by tenant/project vs. cap, downgrade rate, halt rate.

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
| `BUDGET_LEDGER_CREDENTIALS` | Read/write `BUDGET_LEDGER_URI` |
| `PRICING_TABLE_ACCESS` | Signed URL or IAM for `PRICING_TABLE_REF` |
| `MODEL_API_KEY` | Optional agent LLM calls |
| `OPERATOR_OVERRIDE_TOKEN` | Break-glass downgrade; highly restricted rotation |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Gateway + optimizer | 250m | 2 | 256Mi | 1Gi |
| Async breaker worker | 100m | 1 | 128Mi | 512Mi |

Hot path should stay sub-millisecond for cache hits; scale replicas before raising per-pod CPU.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 3s | 200 when pricing + ledger + route schema OK |

Document expected JSON body for `/readyz` (e.g. `{ "ledger": "ok", "pricing_version": "..." }`) in your service contract.
