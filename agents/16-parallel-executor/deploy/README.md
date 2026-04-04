# Deploy: Parallel Executor Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `MODEL_API_ENDPOINT` | yes | Upstream LLM or router endpoint for planning merges |
| `PARALLEL_EXECUTOR_DEFAULT_CONCURRENCY` | yes | Initial cap on concurrent shard executions |
| `PARALLEL_EXECUTOR_TRACE_STORE_REF` | yes | Reference to durable trace storage (URI or vault path) |
| `PARALLEL_EXECUTOR_QUEUE_REF` | yes | Job queue or worker pool endpoint reference |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: queue reachable; trace store readable; model endpoint handshake succeeds (no secrets logged).

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Max shards per `fan_out` | Align with queue capacity (e.g. 200–500) |
| Per-shard timeout | 30s–10m depending on downstream SLA |
| Trace retention | 7–30 days with sampling for high-volume tenants |

## Operational notes

- **Idempotency:** reject duplicate `correlation_id` fan-out unless explicitly allowed by policy.
- **Backpressure:** when queues grow, lower concurrency via `set_concurrency_limit` before shedding load.
- **Observability:** alert on sustained `error_rate` in `trace_aggregate` rollups by `target_tool`.

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
| `MODEL_API_KEY` | Handshake to `MODEL_API_ENDPOINT` (no secrets logged on `/readyz`) |
| `TRACE_STORE_CREDENTIALS` | Access `PARALLEL_EXECUTOR_TRACE_STORE_REF` |
| `QUEUE_CREDENTIALS` | Access `PARALLEL_EXECUTOR_QUEUE_REF` |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Executor service | 1 | 8 | 1Gi | 4Gi |

Worker-heavy; align limits with `PARALLEL_EXECUTOR_DEFAULT_CONCURRENCY` and per-shard memory for in-flight payloads.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when queue + trace store + model handshake OK |

```yaml
readinessProbe:
  httpGet: { path: /readyz, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 5
```
