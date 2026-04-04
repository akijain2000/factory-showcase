# Monitoring: API Test Generator (08)

Observability for OpenAPI/HAR-driven test synthesis (fixture generation, assertion stubs, export). Relaxed error ceiling vs. safety agents; focus on throughput and artifact quality.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ **99.5%** successful HTTP/health checks | Rolling 30 days |
| Latency p50 | < 22 s end-to-end per generation job | Per request |
| Latency p95 | < 68 s | Per request |
| Latency p99 | < **90 s** | Per request |
| Error rate | < **5%** (5xx + parse/export hard failures) | Rolling 24 h |
| Cost per successful request | < $0.40 USD; alert on +25% WoW | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > **10%** for 5 minutes | Page | Severe quality or upstream breakage |
| A2 | Error rate > **5%** for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > **90 s** for 10 minutes | High | CI pipelines waiting on generator |
| A4 | Cost per successful request > $0.40 (1 h rolling) | Warning | Huge specs or repeated retries |
| A5 | Availability < 99.5% over 30 d | Ticket | Contract review |

**PromQL-style examples (adapt to your stack):**

- Error rate: `sum(rate(http_requests_total{agent="api-test-generator",status=~"5.."}[5m])) / sum(rate(http_requests_total{agent="api-test-generator"}[5m])) > 0.10`
- p99 latency: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{agent="api-test-generator"}[5m])) by (le)) > 90`

## Dashboard specification

**Board: API Test Generator – Production**

- **Time ranges:** Last 1 h, 24 h, 7 d (default 24 h).
- **Row 1 – Health:** availability %, jobs/min, error rate %, export success rate.
- **Row 2 – Latency:** p50 / p95 / p99; breakdown by `parse_spec`, `generate_cases`, `render_tests`, model.
- **Row 3 – Cost:** USD/hour, tokens, cost per successful job, avg operations per spec.
- **Row 4 – Artifacts:** tests generated, empty-suite rate, lint failures on output, unsupported operation types.
- **Breakdowns:** `framework` (jest/pytest/etc.), `trace_id`, `spec_hash` (non-sensitive).

## Health check endpoint

`GET /health`

- **200 OK** when healthy; **503** when spec parser or template engine cannot run.

**Response body (JSON):**

```json
{
  "status": "ok",
  "agent": "api-test-generator",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "model_endpoint": "reachable",
    "openapi_parser": "ok",
    "template_engine": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 – Error rate | `deploy/runbooks/api-test-generator-error-rate.md` — invalid OpenAPI, HAR corruption, version skew |
| A3 – Latency p99 | `deploy/runbooks/api-test-generator-latency.md` — spec splitting, cache parsed AST, worker scale |
| A4 – Cost | `deploy/runbooks/api-test-generator-cost.md` — cap operations, dedupe specs |
| A5 – Availability | `deploy/runbooks/api-test-generator-availability.md` — rollbacks, storage for artifacts |

If a runbook file does not exist yet, track it as a follow-up and use `deploy/README.md` until written.
