# Test: step execution failures, retries, and checkpoint timeouts

## Scenario

A workflow run hits transient `execute_step` failures on an idempotent node, exceeds a harness timeout when writing a checkpoint, and requires `resume_from_checkpoint` after a worker crash. The agent must preserve idempotency keys, avoid duplicate side effects, and converge to a terminal checkpoint.

## Setup

- Agent config: `WORKFLOW_CHECKPOINT_REF=kv://wf/harness`, `WORKFLOW_EXECUTOR_REF=exec://mock`, DAG `wf_retry` revision `2` with nodes `fetch`, `transform`, `publish`.
- Tools mocked:
  - `define_dag` → `{ "ok": true, "dag_id": "wf_retry", "revision": 2 }`
  - `execute_step` for `fetch` → first `{ "ok": false, "error": "TRANSIENT" }` with same `idempotency_key`; second `{ "ok": true, "output_ref": "blob_1" }`
  - `checkpoint_state` → first call times out; second `{ "ok": true, "checkpoint_id": "ckpt_9", "cursor": "transform" }`
  - `evaluate_condition` not used in this linear path (or returns pass-through true).
  - `resume_from_checkpoint` → `{ "ok": true, "next_steps": ["transform"], "skipped": ["fetch"] }` when `fetch` completed in store.

## Steps

1. User sends: "Run wf_retry from scratch; fetch may fail once; checkpoint after fetch."
2. Agent should: call `define_dag` if not already defined, start run `run_retry_01`, execute `fetch` with stable `idempotency_key`, retry on `TRANSIENT`.
3. Agent should: call `checkpoint_state` after successful `fetch`; on timeout, retry checkpoint write once.
4. Harness simulates crash before `transform` executes.
5. User sends: "Resume run_retry_01 from latest checkpoint."
6. Agent should: call `resume_from_checkpoint` with `strategy: from_cursor`, skip re-executing `fetch`, run `transform` then `publish`.
7. Agent should: write terminal checkpoint with empty pending steps.

## Expected outcome

- `fetch` executes successfully exactly once across crash (no duplicate success without idempotency match).
- After resume, `next_steps` does not include `fetch` if already completed.
- Final checkpoint exists with no pending nodes.

## Pass criteria

- Harness: two `execute_step` calls for `fetch` maximum (one failure + one success) with identical `idempotency_key`.
- At least two `checkpoint_state` attempts allowed (one timeout + one success) or single success if first succeeds after retry configuration.
- Terminal state: `publish` succeeded exactly once.
