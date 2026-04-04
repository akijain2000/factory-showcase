# Monitoring: Workflow Orchestrator (19)

DAG execution, conditions, checkpoints, resume. One trace per workflow run; spans per `execute_step`.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Orchestrator |
| Latency p50 / p95 | workflow-dependent | 30d | Per-template baselines |
| Error rate | < 1% | 24h | Orchestration errors (not business step failures) |
| Cost per workflow run | Template budget | 30d | Downstream tool + model cost |
| **Step execution p99** | **< 120s** | 24h | Longest single step in run (per template family) |
| **Checkpoint success** | **> 99%** | 30d | Successful `checkpoint_state` / attempts |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| StepP99 | p99 ≥ 120s for template X for 1h | high | Optimize slow step; dependency SLA |
| CheckpointFail | success < 99% over 6h | critical | Storage; idempotency bugs |
| ResumeFailures | `resume_from_checkpoint` errors | page | State corruption; version skew |
| DAGValidationErrors | `define_dag` rejects spike | medium | Authoring bug or bad deploy |
| StuckRuns | no progress > SLO | high | Detector on heartbeats |

## Dashboard spec

- **Row 1:** Active runs, completed/hour, failed runs, paused for condition.
- **Row 2:** Step latency heatmap by step id; checkpoint duration.
- **Row 3:** Checkpoint success %; resume success %.
- **Breakdowns:** Workflow template, tenant, region.

## Health check endpoint spec

- **GET `/healthz`:** orchestrator up.
- **GET `/readyz`:** checkpoint store + DAG registry reachable.
- **GET `/workflows/{id}/status`:** for deep probe (auth-gated).

## Runbook references

- `deploy/README.md`
- `tests/dag-branch-resume.md`
- `tests/test-error-recovery.md`
