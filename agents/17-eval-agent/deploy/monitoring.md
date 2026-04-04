# Monitoring: Eval Agent (17)

Trajectory scoring and rubric calibration. Spans: `score_trajectory`, `calibrate_rubric`, `aggregate_scores`.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Eval API |
| Latency p50 / p95 | 5s / 20s | 24h | Typical scoring batch |
| Error rate | < 1% | 24h | Failed scores / requests |
| Cost per evaluated trajectory | Tracked | 7d | LLM judge + embedding if used |
| **Scoring latency p99** | **< 45s** | 24h | Single trajectory end-to-end score |
| **Calibration drift** | **< 0.1** (e.g. ECE or rubric delta) | 7d | vs golden set; rolling |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| ScoringP99 | p99 ≥ 45s for 20m | high | Judge model latency; batch size |
| CalibrationDrift | drift ≥ 0.1 for 24h | critical | Rerun `calibrate_rubric`; freeze promotions |
| ScoreVarianceAnomaly | sudden spread change | medium | Data shift; adversarial inputs |
| RubricGenFailures | `generate_rubric` errors | page | Template store |
| CostSpike | cost/trajectory > baseline ×1.3 | medium | Model tier review |

## Dashboard spec

- **Row 1:** Trajectories scored/hour, error rate, active rubrics.
- **Row 2:** p50/p95/p99 scoring latency; dimension coverage.
- **Row 3:** Calibration drift trend; human agreement proxy if available.
- **Breakdowns:** Rubric version, domain, difficulty bucket.

## Health check endpoint spec

- **GET `/healthz`:** service up.
- **GET `/readyz`:** golden set accessible; rubric store readable.
- **GET `/rubrics/latest`:** version id for tracing.

## Runbook references

- `deploy/README.md`
- `tests/test-regression.md`
- `tools/calibrate_rubric.md`
