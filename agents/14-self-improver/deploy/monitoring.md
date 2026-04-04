# Monitoring: Self-Improver (14)

Prompt evolution and eval loop. Trace each improvement cycle as one trace with child spans per tool.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99% | 30d | Agent scheduler / runner |
| Latency p95 | N/A primary | — | Cycle-bound metric below |
| Error rate | < 2% | 7d | Failed eval or commit steps |
| Cost per improvement cycle | Cap + alert | 30d | Tokens + compute per cycle |
| **Improvement cycle duration** | **< 300s** p95 | 7d | Start eval → commit/revert decision |
| **Regression rate** | **< 5%** | 30d | Cycles where metrics worsen vs baseline |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| CycleTooSlow | p95 cycle ≥ 300s for 2h | high | Parallelize eval; shrink prompt diff |
| RegressionSpike | regression rate ≥ 5% over 24h | critical | Hold auto-merge; run `test-regression` |
| EvalFailures | eval error rate > 3% for 1h | page | Fixture drift; harness |
| CommitRevertImbalance | revert > 40% of cycles 6h | medium | Rubric or data quality |
| CostPerCycle | > budget cap | medium | Reduce eval breadth |

## Dashboard spec

- **Row 1:** Cycles/hour, success vs revert, regression flag rate.
- **Row 2:** Cycle time p50/p95/p99; span time in `run_evaluation`, `edit_prompt`.
- **Row 3:** Score deltas vs baseline; token usage per cycle.
- **Breakdowns:** Prompt namespace, benchmark suite.

## Health check endpoint spec

- **GET `/healthz`:** runner alive.
- **GET `/readyz`:** eval harness reachable; git/prompt store writable per policy.
- **GET `/status/cycle`:** last cycle outcome + duration (optional).

## Runbook references

- `deploy/README.md`
- `tests/karpathy-keep-vs-discard.md`
- `tests/test-regression.md`
