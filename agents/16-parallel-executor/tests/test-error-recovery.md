# Test: tool failures, retries, timeouts, and circuit breaker

## Scenario

The parallel executor hits transient tool errors, exhausts retries on a hot shard, exceeds per-branch timeouts, and trips a circuit breaker on a downstream dependency. The agent must surface structured failure reasons, respect backoff, avoid unbounded fan-out while the breaker is open, and complete fan-in with explicit degraded status.

## Setup

- Agent config: `PARALLEL_EXECUTOR_MAX_WORKERS=8`, `PARALLEL_EXECUTOR_BRANCH_TIMEOUT_MS=5000`, `PARALLEL_EXECUTOR_MERGE_STRATEGY=partial_ok`, `PARALLEL_EXECUTOR_RETRY_ATTEMPTS=3`, circuit breaker mock opens after 5 failures in a 10s window with half-open probe after 30s.
- Tools mocked:
  - `set_concurrency_limit` → `{ "ok": true, "limit": 4, "effective_limit": 4 }`
  - `fan_out` → first call returns `{ "correlation_id": "corr_fail_01", "submitted": 6, "accepted": true }`; child completions delivered asynchronously to harness.
  - Shard workers: `s0` succeeds; `s1` fails twice with `TRANSIENT` then succeeds; `s2` fails all retries with `TIMEOUT`; `s3` succeeds; `s4` triggers circuit breaker (`CIRCUIT_OPEN`); `s5` never dispatched while breaker open.
  - `trace_aggregate` → spans include `error_kind`, `retry_count`, `timeout_ms` per shard.
  - `handle_partial_failure` → `{ "decision": "retry_failed", "handles": [...] }` then `{ "decision": "abandon_shard", "reason": "circuit_open" }` for `s4`.
  - `fan_in` → `{ "status": "complete_with_errors", "merged": { "metrics": { "succeeded": 4, "failed": 2 } }, "shard_results": [...] }`

## Steps

1. User sends: "Run the six-shard batch `batch_cb_01` with limit 4; some shards will flap—recover what you can and report per-shard outcomes."
2. Agent should: call `set_concurrency_limit` with `limit: 4` and record `effective_limit`.
3. Agent should: call `fan_out` with six shards keyed `s0`…`s5` and a fresh `correlation_id`.
4. Agent should: on `TIMEOUT` for `s2`, invoke `handle_partial_failure` with `policy: retry_failed` until attempts exhaust, then mark shard abandoned with reason `max_retries_exceeded`.
5. Agent should: call `trace_aggregate` with `include_raw_spans: true` after partial completion to correlate retries and timeouts.
6. Agent should: when `s4` returns `CIRCUIT_OPEN`, skip launching substitute work, call `handle_partial_failure` with `policy: fail_fast_branch`, and avoid hammering the mocked dependency.
7. Agent should: call `fan_in` with `merge_strategy: concat`, `fail_if_any_failed: false`, and include partial results plus explicit failure entries for `s2` and `s4`.
8. Agent should: summarize for the user which shards succeeded, which failed after retries, and that the circuit breaker blocked further calls.

## Expected outcome

- `fan_in.merged.metrics.succeeded` is `4` and failed count accounts for timed-out and circuit-blocked shards.
- No tool invocation repeats for `s4` after `CIRCUIT_OPEN` within the same correlation window.
- `trace_aggregate.summary` lists non-zero `error_rate` and per-shard `retry_count` consistent with mocks.
- User-facing summary does not omit failed shard ids or mislabel circuit-breaker state as a generic "unknown error."

## Pass criteria

- Harness records exactly one `fan_out` submission and one `fan_in` for the correlation id, with at most three `handle_partial_failure` calls for `s2` retry policy and one fail-fast decision for `s4`.
- Total wall-clock simulated wait stays under harness cap (no busy-loop retries faster than mock backoff).
- Assertions on `shard_results[].status` pass for all six ids (`ok`, `failed_timeout`, `failed_circuit`, etc.) per fixture schema.
