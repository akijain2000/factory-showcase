# Monitoring: File Organizer Agent

Observability targets and alerting for the workspace file-organizer service (filesystem tools, ReAct loop).

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ 99.5% successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 8 s end-to-end per user turn | Per request |
| Latency p95 | < 18 s | Per request |
| Latency p99 | < 30 s | Per request |
| Error rate | < 2% (5xx + tool hard failures) | Rolling 24 h |
| Cost per successful request | < $0.04 USD (model + tools) | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > 5% for 5 minutes | Page | Any burn before users lose trust in moves |
| A2 | Error rate > 2% for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > 30 s for 5 minutes | Page | UX + timeout risk on `tool_timeout` |
| A4 | Estimated spend > $40 / day (rolling 24 h) | Warning | Runaway model or loop |
| A5 | Availability < 99.5% over 30 d | Ticket | Contract / on-call review |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="file-organizer",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="file-organizer"}[5m])) > 0.05`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="file-organizer"}[5m])) by (le)) > 30`

## Dashboard specification

**Board: File Organizer – Production**

- **Time ranges:** Last 1 h, 24 h, 7 d (default 24 h).
- **Row 1 – Health:** availability %, requests/min, error rate %, active sessions.
- **Row 2 – Latency:** p50 / p95 / p99 series; breakdown by `tool:*` span name from `src/tracing.py`.
- **Row 3 – Cost:** USD/hour, tokens in/out, cost per successful request.
- **Row 4 – Workspace:** tool failures by type (`list_files`, `move_file`, `create_directory`), disk/quota errors.
- **Breakdowns:** `trace_id` drill-down links to structured logs (JSON with `trace_id` / `span_id`).

## Health check endpoint

`GET /health`

- **200 OK** when the process is healthy and required dependencies are satisfied.
- **503** when the agent cannot safely serve traffic (e.g. workspace root missing).

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "file-organizer",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "workspace_root": "readable",
    "model_endpoint": "reachable"
  }
}
```

Include `status: "degraded"` with HTTP 200 only if partial failure is acceptable; otherwise return 503.

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/file-organizer-error-rate.md` — verify permissions, `FILE_ORGANIZER_ROOT`, tool schemas, recent prompt changes |
| A3 – Latency p99 | `deploy/runbooks/file-organizer-latency.md` — disk contention, large trees, reduce `max_steps`, check model latency |
| A4 – Cost | `deploy/runbooks/file-organizer-cost.md` — token usage, loop detection, tighten budgets in `AgentConfig` |
| A5 – Availability | `deploy/runbooks/file-organizer-availability.md` — deploy rollbacks, dependency outages |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
