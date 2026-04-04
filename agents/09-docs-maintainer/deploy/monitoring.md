# Monitoring: Docs Maintainer Agent

Documentation refresh and consistency checks.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ 99.5% | Rolling 30 days |
| Latency p50 | < 18 s | Per docs job |
| Latency p95 | < 40 s | Per job |
| Latency p99 | < 60 s | Per job |
| Error rate | < 3% | Rolling 24 h |
| Cost per successful request | < $0.10 USD | Daily rollup |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > 5% for 5 minutes | Page | Broken doc pipelines |
| A2 | Error rate > 3% for 25 minutes | Warning | SLO burn |
| A3 | Latency p99 > 60 s for 5 minutes | Warning | Large-repo sync |
| A4 | Spend > $90 / day | Warning | Full-site regen loops |

## Dashboard specification

**Board: Docs Maintainer – Production**

- **Time ranges:** 1 h, 24 h, 30 d.
- **Row 1:** PRs or commits processed, error rate, drift detections.
- **Row 2:** p50 / p95 / p99; split static site vs. monorepo paths.
- **Row 3:** Tokens, $/PR, link-check failure counts.
- **Row 4:** VCS rate limits, merge conflicts deferred.
- **Breakdowns:** By repo / doc set.

## Health check endpoint

`GET /health`

```json
{
  "status": "ok",
  "agent": "docs-maintainer",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "git_remote": "reachable",
    "model_endpoint": "reachable",
    "publish_target": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 | `deploy/runbooks/docs-maintainer-error-rate.md` |
| A3 | `deploy/runbooks/docs-maintainer-latency.md` |
| A4 | `deploy/runbooks/docs-maintainer-cost.md` |
