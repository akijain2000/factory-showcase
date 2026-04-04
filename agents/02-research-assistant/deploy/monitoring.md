# Monitoring: Research Assistant (02)

Observability targets and alerting for the research assistant service (web retrieval, synthesis, citations).

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ 99.5% successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 20 s end-to-end per request | Per request |
| Latency p95 | < 45 s | Per request |
| Latency p99 | < **60 s** | Per request |
| Error rate | < **2.5%** (5xx + tool hard failures) | Rolling 24 h |
| Cost per successful request | < **$0.50 USD** (model + retrieval + tools) | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > 5% for 5 minutes | Page | User-visible failures; burn before trust loss |
| A2 | Error rate > **2.5%** for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > **60 s** for 5 minutes | Page | Timeout risk; degraded research loops |
| A4 | Cost per successful request > **$0.50** (1 h rolling) or daily spend anomaly +30% WoW | Warning | Runaway retrieval or model usage |
| A5 | Availability < 99.5% over 30 d | Ticket | Contract / on-call review |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="research-assistant",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="research-assistant"}[5m])) > 0.05`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="research-assistant"}[5m])) by (le)) > 60`
- Cost: `sum(rate(request_cost_usd_total{agent="research-assistant"}[1h])) / sum(rate(http_requests_total{agent="research-assistant",status="2xx"}[1h])) > 0.50`

## Dashboard specification

**Board: Research Assistant – Production**

- **Time ranges:** Last 1 h, 24 h, 7 d (default 24 h).
- **Row 1 – Health:** availability %, requests/min, error rate %, active sessions.
- **Row 2 – Latency:** p50 / p95 / p99 series; breakdown by span (`retrieve`, `synthesize`, `citation_check`, model calls).
- **Row 3 – Cost:** USD/hour, tokens in/out, **cost per successful request**, retrieval API call volume.
- **Row 4 – Sources:** fetch failures by domain, rate-limit events, cache hit ratio (if applicable).
- **Breakdowns:** `trace_id` drill-down to structured logs; optional `tenant_id` / `session_id`.

## Health check endpoint

`GET /health`

- **200 OK** when the process is healthy and required dependencies are satisfied.
- **503** when the agent cannot safely serve traffic (e.g. model or search backend unreachable).

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "research-assistant",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "retrieval_backend": "reachable"
  }
}
```

Include `status: "degraded"` with HTTP 200 only if partial failure is acceptable; otherwise return 503.

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/research-assistant-error-rate.md` — retrieval quotas, auth, prompt/tool schema drift |
| A3 – Latency p99 | `deploy/runbooks/research-assistant-latency.md` — slow sources, batch size, model region, `max_steps` |
| A4 – Cost | `deploy/runbooks/research-assistant-cost.md` — token ceilings, citation depth, cache policy |
| A5 – Availability | `deploy/runbooks/research-assistant-availability.md` — deploy rollbacks, dependency outages |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
