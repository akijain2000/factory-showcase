# Monitoring: Learning Tutor Agent

Interactive tutoring — low latency matters more than batch throughput.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ 99.5% | Rolling 30 days |
| Latency p50 | < 4 s | Per learner turn |
| Latency p95 | < 10 s | Per turn |
| Latency p99 | < 15 s | Per turn |
| Error rate | < 2% | Rolling 24 h |
| Cost per successful request | < $0.03 USD | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > 5% for 5 minutes | Page | Broken sessions |
| A2 | Error rate > 2% for 20 minutes | Warning | SLO burn |
| A3 | Latency p99 > 15 s for 5 minutes | Page | Perceived “laggy tutor” |
| A4 | Spend > $50 / day | Warning | Viral traffic or prompt bloat |

## Dashboard specification

**Board: Learning Tutor – Production**

- **Time ranges:** 1 h, 24 h, 7 d.
- **Row 1:** Active learners, turns/min, error rate, session length.
- **Row 2:** p50 / p95 / p99; breakdown by tool (`assess_knowledge`, `generate_exercise`, `store_progress`).
- **Row 3:** Tokens per turn, hint vs. solution ratio (product metrics).
- **Row 4:** Content moderation / policy flags if applicable.
- **Breakdowns:** By locale, grade band, or curriculum module.

## Health check endpoint

`GET /health`

```json
{
  "status": "ok",
  "agent": "learning-tutor",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "progress_store": "reachable",
    "model_endpoint": "reachable"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 | `deploy/runbooks/learning-tutor-error-rate.md` |
| A3 | `deploy/runbooks/learning-tutor-latency.md` — model region, KV cache, trim context |
| A4 | `deploy/runbooks/learning-tutor-cost.md` |
