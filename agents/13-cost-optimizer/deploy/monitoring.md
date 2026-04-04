# Monitoring: Cost Optimizer (13)

Model routing and budget enforcement. Attribute spans with `tokens.*` and `cost.usd` via `cost_tracked` on tool handlers.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Routing + budget API |
| Latency p50 / p95 | 100ms / 500ms | 24h | Non-LLM control plane |
| Error rate | < 0.5% | 24h | Failed routes / checks |
| Cost per routed request | Tracked; alert on drift | 7d | Actual vs estimated |
| **Routing latency p99** | **< 2s** | 24h | Includes `route_to_model` decision path |
| **Budget accuracy** | **> 95%** | 7d | Estimated vs actual spend on held-out sample |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| RoutingP99 | p99 ≥ 2s for 15m | high | Latency on policy store; cache hit rate |
| BudgetAccuracyLow | rolling accuracy ≤ 93% for 6h | critical | Recalibrate estimates; audit `track_tokens` |
| BudgetExhaustionSpike | sudden jump in downgrades | medium | Expected vs attack; see tests |
| RouteErrors | error rate ≥ 1% for 10m | page | Provider outages; fallback path |
| CostDrift | actual > estimate by > 10% | medium | Price table refresh |

## Dashboard spec

- **Row 1:** Routes/sec, downgrade rate, budget checks/sec, errors.
- **Row 2:** p50/p95/p99 routing latency; cache hits for policy.
- **Row 3:** Budget accuracy trend; USD saved vs premium path (estimated).
- **Breakdowns:** Model tier, tenant, task type.

## Health check endpoint spec

- **GET `/healthz`:** up.
- **GET `/readyz`:** pricing table + budget store reachable; dry-run `check_budget`.
- **GET `/version`:** policy/ruleset version for trace correlation.

## Runbook references

- `deploy/README.md`
- `tests/budget-exhaustion-downgrade.md`
- `tests/test-error-recovery.md`
