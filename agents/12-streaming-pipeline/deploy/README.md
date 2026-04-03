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
