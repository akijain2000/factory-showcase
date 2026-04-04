# Monitoring: Incident Responder (07)

Observability for **urgent** incident triage and first-response automation. Highest availability target and **lowest latency p99** in this set.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ **99.99%** successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 2 s end-to-end per request | Per request |
| Latency p95 | < 6 s | Per request |
| Latency p99 | < **10 s** | Per request |
| Error rate | < **1%** (5xx + paging/integrations hard failures) | Rolling 24 h |
| Cost per successful request | < $0.08 USD; alert on +30% WoW | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > **2%** for 3 minutes | Page | Urgent path degraded |
| A2 | Error rate > **1%** for 10 minutes | Warning | SLO burn |
| A3 | Latency p99 > **10 s** for 3 minutes | Page | **Urgent** — on-call tooling must stay fast |
| A4 | Latency p95 > **6 s** for 10 minutes | Warning | Early regression signal |
| A5 | Cost per successful request > $0.08 (1 h rolling) | Warning | Unexpected model or webhook volume |
| A6 | Availability < **99.99%** over 30 d | Page | Executive / incident-command review |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="incident-responder",status=~"5.."}[3m])) / sum(rate(http_requests_total{agent="incident-responder"}[3m])) > 0.02`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="incident-responder"}[3m])) by (le)) > 10`

## Dashboard specification

**Board: Incident Responder – Production**

- **Time ranges:** Last 15 m, 1 h, 24 h (default 1 h for urgency).
- **Row 1 – Health:** availability %, requests/min, error rate %, **paging provider** delivery success.
- **Row 2 – Latency:** p50 / p95 / p99 with SLO lines at 2 s / 6 s / 10 s; breakdown by `classify`, `enrich`, `notify`, `model` (if any).
- **Row 3 – Cost:** USD/hour, cost per successful request, external API call rate.
- **Row 4 – Incidents:** creations/hour, auto-ack rate, escalations, integration errors (Slack/PagerDuty/etc.).
- **Breakdowns:** `severity`, `service`, `trace_id`; redact PII in drill-downs.

## Health check endpoint

`GET /health`

- **200 OK** when healthy; **503** when paging or critical integrations cannot be reached.

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "incident-responder",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "paging_webhook": "reachable",
    "incident_store": "reachable"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/incident-responder-error-rate.md` — webhook secrets, rate limits, idempotency |
| A3, A4 – Latency | `deploy/runbooks/incident-responder-latency.md` — cold starts, dependency circuit breakers, fast-path cache |
| A5 – Cost | `deploy/runbooks/incident-responder-cost.md` — suppress noisy automations; batch enrichment |
| A6 – Availability | `deploy/runbooks/incident-responder-availability.md` — multi-region failover; **urgent** comms template |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
