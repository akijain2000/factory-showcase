# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

`run_evaluation` times out once, `compare_metrics` returns `METRICS_STORE_UNAVAILABLE`, and the eval runner circuit opens. The agent must not commit a candidate and must backoff/retry within governance limits.

## Setup

- Agent config: `PROMPT_REGISTRY_URI=mock://prompts`, `EVAL_SUITE_REF=suite/bench-2026.04.01`, `METRICS_STORE_URI=mock://metrics`, breaker: three consecutive eval failures open circuit for 10 minutes.
- Tools mocked:
  - `read_current_prompt`: `{ "prompt_id": "inner/task-router", "version": "2026.04.03-11", "content_hash": "h0" }`.
  - `edit_prompt`: `{ "candidate_id": "cand_88", "diff_unified": "@@ ...", "ok": true }`.
  - `run_evaluation`: first → timeout; second → `{ "run_id": "run_901", "status": "complete" }`.
  - `compare_metrics`: first → `{ "error": "METRICS_STORE_UNAVAILABLE", "retryable": true }`; second → `{ "gates_pass": true, "deltas": { "task_success": 0.01 } }`.
  - `commit_or_revert`: returns error if called while circuit open or before successful compare.

## Steps

1. User sends: "Try a small clarity tweak on inner/task-router and promote if evals are neutral or better."
2. Agent should: `read_current_prompt` then `edit_prompt` with rationale-bearing diff.
3. Agent should: `run_evaluation` with retry on timeout, bounded by policy.
4. Agent should: `compare_metrics` with retry on metrics store flake; never `commit_or_revert keep` without a successful compare.
5. Agent should: if circuit opens (extended variant), `commit_or_revert` with hold/abort path per harness—not keep.

## Expected outcome

- Candidate exists only after successful `edit_prompt`; eval run completes on second attempt in the base fixture.
- No `commit_or_revert` with `decision: keep` until `compare_metrics` returns success object.
- User summary reflects transient failures honestly.

## Pass criteria

- Ordered gate: `compare_metrics` success precedes any `commit_or_revert` with `decision: keep`.
- `run_evaluation` invocation count ≥ 2 in timeout script.
- Measurable: if extended circuit-open variant runs, zero promotions and explicit operator message.
