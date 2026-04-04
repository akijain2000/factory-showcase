# Deploy: Streaming Pipeline Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `EVENT_BUS_ENDPOINT` | yes | Broker or gateway for `emit_event` / subscriptions |
| `STREAM_ROOT_SCOPE_ID` | yes | Default root scope; protect from accidental mass cancel |
| `BACKPRESSURE_METRICS_REF` | yes | Metrics store or broker admin API for `inspect_backpressure` |
| `INTERCEPTOR_REGISTRY_URI` | yes | Source of truth for ordered interceptor registrations |
| `MODEL_API_ENDPOINT` | optional | Agent reasoning endpoint (secrets via host only) |

## Health checks

- **/healthz:** process up; interceptor registry reachable.
- **/readyz:** can read lag for configured `consumer_group` within timeout; cancel API not in degraded mode.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Interceptor `timeout_ms` | 1–5s hot path; longer only on async handoff |
| `emit_event` payload | Cap bytes per org policy; reject oversize at ingress |
| Concurrent `cancel_subtree` | Limit per tenant to avoid coordination storms |

## Operations

- **Upgrades:** dual-register interceptors during rolling deploy; verify `effective_order` in staging.
- **Incidents:** pair `inspect_backpressure` with partition-level charts; prefer subtree cancel before global pause.
- **Security:** enforce `producer_id` authentication at bus ingress; reject unsigned `emit_event` in regulated environments.

## Observability

- Metrics: `interceptor_latency_ms`, `cancel_subtree_total`, `aggregate_state_bytes`, `consumer_lag_seconds`.
- Logs: correlate `causation_id` across emit → aggregate → consumer spans.

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
# EVENT_BUS_* credentials via secret store at runtime
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `EVENT_BUS_AUTH` | SASL / API key / client cert for broker |
| `INTERCEPTOR_REGISTRY_CREDENTIALS` | Read/write `INTERCEPTOR_REGISTRY_URI` |
| `MODEL_API_KEY` | If `MODEL_API_ENDPOINT` is used for agent reasoning |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Agent + bus client | 500m | 4 | 512Mi | 2Gi |

Increase limits when hosting large in-memory aggregate windows; prefer spill-to-store for unbounded state.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 15s | 10s | 2s | HTTP 200, process up |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when registry + consumer lag probe pass |

Kubernetes example:

```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 15
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /readyz, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 5
```
