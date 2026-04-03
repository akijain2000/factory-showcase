# Test: DAG with conditional branch, checkpoint, and resume

## Scenario

A three-layer DAG runs through ingest and validation, evaluates a condition to choose between `short_path` and `long_path`, checkpoints after the branch step, simulates a worker crash before `publish`, and resumes without redoing completed side effects.

## Given

- DAG `wf_demo` revision `1` with nodes: `ingest`, `validate`, `branch_gate`, `short_path`, `long_path`, `publish`.
- Edges: `ingest → validate → branch_gate`; `branch_gate → short_path` when condition `low_volume` is true; `branch_gate → long_path` when false; both merge to `publish`.
- `evaluate_condition` expression ref `low_volume` returns true when `facts.order_count <= 10`.
- `execute_step` for `ingest` and `validate` is configured to succeed once and **fail on unintended replay** without matching `idempotency_key`.

## When

- The agent calls `define_dag` with the graph above.
- The agent starts run `run_xyz` and executes `ingest` then `validate` with stable `idempotency_key` values.
- The agent calls `evaluate_condition` with `facts: {"order_count": 4}` and records the branch decision.
- The agent executes `short_path` and calls `checkpoint_state` with `cursor` pointing at `publish` as the only pending step.
- The harness terminates the worker before `publish` executes.
- The agent calls `resume_from_checkpoint` with `strategy: from_cursor` and the latest `checkpoint_id`.

## Then

- Topological layers match expectations (`ingest`+`validate` may share a layer only if policy allows; otherwise sequential order is respected).
- `branch_gate` selects `short_path` and never executes `long_path`.
- After resume, `next_steps` equals `["publish"]` and `ingest`/`validate`/`short_path` appear in `skipped` or completed lists without duplicate side effects.
- Final `publish` execution succeeds and a terminal checkpoint exists with no pending steps.
