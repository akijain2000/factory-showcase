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
