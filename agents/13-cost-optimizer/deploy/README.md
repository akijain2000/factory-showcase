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
