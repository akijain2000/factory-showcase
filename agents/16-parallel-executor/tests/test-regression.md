# Test: all shards fail, inconsistent shard schema, concurrency limit exceeded

## Scenario

Regression harness covers three production-like faults: (1) every shard in a fan-out fails so fan-in must degrade cleanly; (2) one shard returns a payload whose fields disagree with the merge contract (inconsistent schema); (3) the user or planner requests more concurrent branches than `effective_limit` allows after `set_concurrency_limit`.

## Setup

- Agent config: `PARALLEL_EXECUTOR_MAX_WORKERS=8`, `PARALLEL_EXECUTOR_MERGE_STRATEGY=partial_ok`, `PARALLEL_EXECUTOR_RETRY_ATTEMPTS=1`.
- Tools mocked:
  - `set_concurrency_limit` with `limit: 2` → `{ "ok": true, "effective_limit": 2 }`
  - `fan_out` for case (1): all shards complete with `status: failed`, error codes distinct per shard.
  - `fan_out` for case (2): shards `a`,`b` succeed; shard `c` returns `{ "rows": [...] }` while others return `{ "items": [...] }` (schema mismatch at fan-in).
  - `fan_out` for case (3): if submission includes more than `effective_limit` runnable branches without queueing, mock returns `{ "accepted": false, "reason": "CONCURRENCY_LIMIT_EXCEEDED", "effective_limit": 2 }`.
  - `trace_aggregate` → full error summary for case (1); tagging `schema_conflict: true` on case (2) when integrator supports it.
  - `handle_partial_failure` → `abandon_batch` or per-shard `abandon_shard` for case (1); `normalize_or_reject` suggestion for case (2).
  - `fan_in` → case (1): `{ "status": "failed", "merged": null, "shard_results": [...all failed...] }`; case (2): `{ "ok": false, "reason": "INCONSISTENT_MERGE_SCHEMA" }`; case (3): not reached until batch resized or queued.

## Steps

1. User sends: "Fan out shards s1–s4 with limit 2; I expect everything may fail—still aggregate errors."
2. Agent should: call `set_concurrency_limit` then `fan_out` with at most two concurrent executions per mock semantics (or split into waves); when all shards fail, call `trace_aggregate` and `fan_in` with `fail_if_any_failed: true` or document `complete_with_errors` per policy.
3. User sends: "Merge branches a,b,c—the third file used a different JSON shape on purpose."
4. Agent should: call `fan_in`, receive `INCONSISTENT_MERGE_SCHEMA`, and either coerce via an explicit normalizer tool (if available) or refuse merge and list conflicting keys (`rows` vs `items`).
5. User sends: "Actually run ten shards at once with the same limit 2—override the cap."
6. Agent should: not override cap; receive `CONCURRENCY_LIMIT_EXCEEDED` or enqueue shards; never silently drop shards without user-visible accounting.

## Expected outcome

- Case (1): User sees all four failure reasons; no empty success message; `merged` is absent or clearly marked failed.
- Case (2): No silent concatenation of incompatible arrays; conflict reason is named in the assistant reply.
- Case (3): No more than `effective_limit` concurrent executions without explicit queue semantics; user informed how remaining shards will run.

## Pass criteria

- Harness counts: case (1) `fan_in` status in `{"failed","complete_with_errors"}` with `succeeded: 0`.
- Case (2): exactly one `fan_in` rejection with `INCONSISTENT_MERGE_SCHEMA` (or equivalent) before any user-visible "success."
- Case (3): either batched waves totaling ten shards or an explicit limit error—no burst of ten parallel mock executions.
