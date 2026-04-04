# Monitoring: Context Engineer (11)

Observability for ACE loops (curate → evaluate → reflect → compress). Uses `src/tracing.py` (`TRACE_EXPORTER=console|otlp|none`, W3C `traceparent` via `inject_carrier` / `extract_carrier`).

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Successful turn completion vs. total requests |
| Latency p50 / p95 / p99 | 4s / 12s / **< 20s** | 7d rolling | End-to-end request; spans: `tool:*`, model calls |
| Error rate | < 1% | 24h | 5xx + unhandled tool errors / total |
| Cost per request | Baseline + alert on +25% WoW | 7d | Sum `cost.usd` from `cost_tracked` / successful requests |
| **Context quality** | **> 0.8** (rolling mean) | 7d | From `evaluate_context_quality` scores; min sample 50/session |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| LatencySLOBurn | p99 ≥ 20s for 15m | page | Scale workers; check model latency; see runbook |
| QualityDrop | context quality ≤ 0.75 for 1h | critical | Pause auto-promotion; inspect reflections |
| ErrorSpike | error rate ≥ 2% for 10m | high | Check `CONTEXT_STORE_URI`, rate limits |
| CostAnomaly | cost/request > 1.25× 7d baseline | medium | Review compression triggers; token ceiling |
| Availability | success rate < 99% for 30m | page | Dependency health; circuit limits |

## Dashboard spec

- **Row 1:** RPS, availability %, error rate, p50/p95/p99 latency.
- **Row 2:** Context quality (gauge + trend), tokens in/out per request, `cost.usd` sum.
- **Row 3:** Span breakdown: `curate`, `evaluate`, `reflect`, `compress`, model spans.
- **Breakdowns:** By `tenant_id`, `bundle_id`, `PROMPT_VERSION_NAMESPACE`.

## Health check endpoint spec

- **GET `/healthz`:** process up; returns `200` with `{"status":"ok"}`.
- **GET `/readyz`:** `CONTEXT_STORE_URI` reachable; prompt registry readable; optional dependency ping.
- **GET `/livez`:** same as liveness in `deploy/README.md` (worker heartbeat if async tier enabled).

Expose `trace_id` from active span in response headers when handling debug traffic (`X-Trace-Id`).

## Runbook references

- `deploy/README.md` — env vars, scaling, security.
- `tests/test-error-recovery.md` — degradation paths.
- `tests/test-regression.md` — quality regressions.
