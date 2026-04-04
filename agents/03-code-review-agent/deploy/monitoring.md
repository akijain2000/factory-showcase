# Monitoring: Code Review Agent (03)

Observability targets and alerting for automated code review (diff analysis, static hints, LLM commentary).

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ **99.5%** successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 12 s end-to-end per review | Per request |
| Latency p95 | < 32 s | Per request |
| Latency p99 | < **45 s** | Per request |
| Error rate | < **3%** (5xx + unhandled tool/parser failures) | Rolling 24 h |
| Cost per successful request | < $0.35 USD (model + diff tooling); alert on +25% WoW | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > **6%** for 5 minutes | Page | Severe burn |
| A2 | Error rate > **3%** for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > **45 s** for 5 minutes | Page | CI/review UX timeouts |
| A4 | Cost per successful request > $0.35 (1 h rolling) or +25% vs 7 d baseline | Warning | Large diffs or runaway loops |
| A5 | Availability < 99.5% over 30 d | Ticket | Contract review |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="code-review-agent",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="code-review-agent"}[5m])) > 0.06`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="code-review-agent"}[5m])) by (le)) > 45`

## Dashboard specification

**Board: Code Review Agent – Production**

- **Time ranges:** Last 1 h, 24 h, 7 d (default 24 h).
- **Row 1 – Health:** availability %, reviews/min, error rate %, queue depth (if async).
- **Row 2 – Latency:** p50 / p95 / p99; breakdown by `parse_diff`, `model`, `format_findings`.
- **Row 3 – Cost:** USD/hour, tokens in/out, cost per successful review, avg diff size (lines).
- **Row 4 – Quality signals:** parser errors, empty findings rate, timeout count by reason.
- **Breakdowns:** `repo`, `language`, `trace_id` to logs.

## Health check endpoint

`GET /health`

- **200 OK** when healthy; **503** when unsafe to serve (e.g. git/diff tooling or model unavailable).

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "code-review-agent",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "diff_toolchain": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/code-review-agent-error-rate.md` — malformed diffs, token limits, VCS access |
| A3 – Latency p99 | `deploy/runbooks/code-review-agent-latency.md` — diff chunking, model latency, parallelism |
| A4 – Cost | `deploy/runbooks/code-review-agent-cost.md` — max diff bytes, summarization tiers |
| A5 – Availability | `deploy/runbooks/code-review-agent-availability.md` — rollbacks, dependency health |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
