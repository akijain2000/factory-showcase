# Test: concurrent fan-out with partial failure recovery

## Scenario

A batch of independent shard tasks runs under a shared correlation id; one shard fails while others succeed. The agent aggregates traces, applies `retry_failed`, and completes fan-in with explicit error accounting.

## Given

- Concurrency limit is set to `4`.
- Ten shards are submitted via `fan_out` with distinct `sort_key` values `s00` … `s09`.
- Shard `s03` is configured by the test harness to fail on first attempt and succeed on second.
- Trace store is empty for the correlation id at test start.

## When

- The agent calls `set_concurrency_limit` with `limit: 4`.
- The agent calls `fan_out` with all ten shards and a fresh `correlation_id`.
- After child completion signals, the agent calls `trace_aggregate` with `include_raw_spans: false`.
- The agent calls `handle_partial_failure` with `policy: retry_failed` targeting the failed shard id.
- The agent calls `fan_in` with `merge_strategy: concat`, `fail_if_any_failed: false`, and full `shard_results` after retries.

## Then

- `trace_aggregate.summary.error_rate` reflects the initial failure before retry completes.
- `handle_partial_failure` returns `decision: retry_failed` with a new `handle` for the retried shard.
- Final `fan_in.status` is `complete` or `complete_with_errors` per harness semantics, and `merged.metrics.succeeded` equals `10`.
- Ordering of merged items matches lexical `sort_key` order.
- No shard failure is omitted from the final structured summary shown to the user.
