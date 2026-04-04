# Monitoring: Parallel Executor (16)

Fan-out / fan-in execution with partial failure handling. Trace each branch as child spans under one root trace.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Executor service |
| Latency p50 / p95 | task-dependent | 24h | Per-branch where applicable |
| Error rate | < 2% | 24h | Total branch failures / branches |
| Cost per fan-out batch | Baseline + alert | 7d | Aggregate `cost.usd` across branches |
| **Fan-out latency p99** | **< 60s** | 24h | Schedule → all branches settled (success or classified partial) |
| **Partial failure recovery** | **> 90%** | 7d | Recovered or degraded-safe outcomes / partial failures |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| FanOutP99 | p99 ≥ 60s for 15m | high | Concurrency limits; straggler detection |
| RecoveryLow | recovery ≤ 88% for 6h | critical | Review `handle_partial_failure`; aggregate logic |
| BranchErrorStorm | > 5% branch hard fails 10m | page | Downstream dependency |
| ConcurrencySaturation | limit hits sustained | medium | Raise cap or shed load |
| TraceFragmentation | missing child spans | low | Instrumentation gap |

## Dashboard spec

- **Row 1:** Fan-outs/hour, branches per fan-out, partial vs full failure counts.
- **Row 2:** p50/p95/p99 fan-out latency; straggler tail (max branch time).
- **Row 3:** Recovery success rate; `trace_aggregate` duration.
- **Breakdowns:** Task type, tenant, concurrency tier.

## Health check endpoint spec

- **GET `/healthz`:** executor up.
- **GET `/readyz`:** thread/process pool accepting work; dependency smoke.
- **GET `/metrics/pool`:** active workers, queue depth (optional).

## Runbook references

- `deploy/README.md`
- `tests/test-error-recovery.md`
- `tools/handle_partial_failure.md`
