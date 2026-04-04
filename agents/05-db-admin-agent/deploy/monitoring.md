# Monitoring: DB Admin Agent (05)

Observability for **safety-critical** database administration assistance (read-heavy diagnostics, guarded write proposals). Tightest error budget in this catalog.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ **99.9%** successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 25 s end-to-end per request | Per request |
| Latency p95 | < 70 s | Per request |
| Latency p99 | < **90 s** | Per request |
| Error rate | < **0.5%** (5xx + tool/connection hard failures) | Rolling 24 h |
| Cost per successful request | < $0.40 USD; alert on +20% WoW | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > **1%** for 5 minutes | Page | **Safety-critical** — wrong or failed DB operations context |
| A2 | Error rate > **0.5%** for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > **90 s** for 10 minutes | High | Risk of client timeouts mid-operation |
| A4 | Cost per successful request > $0.40 (1 h rolling) | Warning | Runaway explain plans or log pulls |
| A5 | Availability < **99.9%** over 30 d | Page | Contract / on-call (**safety-critical**) |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="db-admin-agent",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="db-admin-agent"}[5m])) > 0.01`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="db-admin-agent"}[5m])) by (le)) > 90`

## Dashboard specification

**Board: DB Admin Agent – Production**

- **Time ranges:** Last 1 h, 24 h, 30 d.
- **Row 1 – Health:** availability %, requests/min, error rate %, **read-only mode** indicator (if enforced).
- **Row 2 – Latency:** p50 / p95 / p99; breakdown by `connect`, `query`, `explain`, `model`.
- **Row 3 – Cost:** USD/hour, tokens, cost per successful request, rows scanned estimates (if exported).
- **Row 4 – Safety:** denied writes, policy blocks, credential rotation errors, connection pool saturation.
- **Breakdowns:** `cluster_id` (non-secret label), `trace_id`; never log secrets or full connection strings.

## Health check endpoint

`GET /health`

- **200 OK** when healthy; **503** when DB connectivity or mandatory guardrails are unavailable.

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "db-admin-agent",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "database": "reachable",
    "read_only_enforcement": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/db-admin-agent-error-rate.md` — credentials, network, query timeouts, pool limits |
| A3 – Latency p99 | `deploy/runbooks/db-admin-agent-latency.md` — slow queries, replica lag, reduce scan scope |
| A4 – Cost | `deploy/runbooks/db-admin-agent-cost.md` — token limits, result set caps |
| A5 – Availability | `deploy/runbooks/db-admin-agent-availability.md` — **safety-critical** rollback; DBA escalation |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
