# Monitoring: Migration Planner (04)

Observability for **safety-critical** migration planning (schema analysis, risk assessment, rollout steps). Stricter availability and error targets than general-purpose agents.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ **99.9%** successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 40 s end-to-end per plan | Per request |
| Latency p95 | < 90 s | Per request |
| Latency p99 | < **120 s** | Per request |
| Error rate | < **1%** (5xx + validation/planner hard failures) | Rolling 24 h |
| Cost per successful request | < $0.80 USD; alert on +20% WoW | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > **2%** for 5 minutes | Page | Safety-critical; incorrect or missing plans |
| A2 | Error rate > **1%** for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > **120 s** for 10 minutes | High | Planning timeouts; risk of partial outputs |
| A4 | Cost per successful request > $0.80 (1 h rolling) | Warning | Oversized context or loop |
| A5 | Availability < **99.9%** over 30 d | Page | Contract / exec review (**safety-critical**) |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="migration-planner",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="migration-planner"}[5m])) > 0.02`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="migration-planner"}[5m])) by (le)) > 120`

## Dashboard specification

**Board: Migration Planner – Production**

- **Time ranges:** Last 1 h, 24 h, 30 d (emphasize 30 d for 99.9% SLO).
- **Row 1 – Health:** availability %, plans/min, error rate %, **safety flag**: plans emitted without human-review gate (if applicable).
- **Row 2 – Latency:** p50 / p95 / p99; breakdown by `analyze_schema`, `risk_model`, `generate_steps`, model.
- **Row 3 – Cost:** USD/hour, tokens, cost per successful plan, schema object counts.
- **Row 4 – Safety:** validation failures, rollback-step coverage, ambiguous dependency warnings.
- **Breakdowns:** `environment` (staging/prod metadata only), `trace_id`, `plan_id`.

## Health check endpoint

`GET /health`

- **200 OK** when healthy; **503** when planning must not proceed (e.g. schema connector or policy engine down).

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "migration-planner",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "schema_metadata": "reachable",
    "policy_engine": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/migration-planner-error-rate.md` — connector auth, DDL parse errors, prompt version |
| A3 – Latency p99 | `deploy/runbooks/migration-planner-latency.md` — narrow schema scope, cache metadata, model tier |
| A4 – Cost | `deploy/runbooks/migration-planner-cost.md` — context windows, incremental analysis |
| A5 – Availability | `deploy/runbooks/migration-planner-availability.md` — freeze risky deploys; rollback; **safety-critical** comms |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
