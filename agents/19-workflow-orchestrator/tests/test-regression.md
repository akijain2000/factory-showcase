# Test: DAG cycle detection, missing step dependency, checkpoint corruption

## Scenario

Regression triple: (1) `define_dag` must reject or repair cycles; (2) `execute_step` ordering must not run a node before unsatisfied dependencies; (3) corrupted checkpoint payloads cannot resume into an inconsistent graph state.

## Setup

- Agent config: topological validator strict mode on; dependency resolver uses declared edges only.
- Tools mocked:
  - `define_dag` → on cycle `ingest → validate → ingest`, returns `{ "ok": false, "error": "DAG_CYCLE_DETECTED", "cycle": ["ingest","validate","ingest"] }`.
  - `define_dag` → valid acyclic graph `wf_dep` with `publish` depending on `sign` which depends on `build`.
  - `execute_step` → if `publish` called before `sign` complete in run state, returns `{ "ok": false, "error": "DEPENDENCY_NOT_SATISFIED", "missing": ["sign"] }`.
  - `checkpoint_state` → can return `{ "ok": true, "checkpoint_id": "ckpt_good" }` for valid writes.
  - `resume_from_checkpoint` → for `checkpoint_id: ckpt_corrupt`, returns `{ "ok": false, "error": "CHECKPOINT_CORRUPT", "details": "crc_mismatch" }`.

## Steps

1. User sends: "Register DAG with edges ingest→validate→ingest for run demo."
2. Agent should: call `define_dag`, receive `DAG_CYCLE_DETECTED`, and explain the cycle path to the user without persisting bad graph.
3. User sends: "Use wf_dep; run publish first, skip build/sign—they already happened elsewhere."
4. Agent should: call `execute_step` for `publish`, receive `DEPENDENCY_NOT_SATISFIED` with `missing: ["sign"]` (and possibly `build`), then schedule prerequisites instead of forcing publish.
5. User sends: "Checkpoint is ckpt_corrupt—resume run_fix from it."
6. Agent should: call `resume_from_checkpoint`, receive `CHECKPOINT_CORRUPT`, refuse to continue blindly, and suggest restarting from last good checkpoint or rebuilding DAG run.
7. User sends: "If you find ckpt_good in the store, resume from that instead."
8. Agent should: on successful resume, list consistent `next_steps` matching dependency closure.

## Expected outcome

- Cyclic DAG never enters the workflow store as `ok: true` in harness.
- `publish` never succeeds before `sign` in recorded run state for the dependency test.
- Corrupt checkpoint path produces user-visible error mentioning corruption, not a partial random step execution.

## Pass criteria

- `define_dag` failure with `DAG_CYCLE_DETECTED` recorded once.
- At least one `execute_step` denial with `DEPENDENCY_NOT_SATISFIED` before dependencies complete.
- `resume_from_checkpoint` with `ckpt_corrupt` fails exactly once with `CHECKPOINT_CORRUPT` before any successful side-effect steps post-resume.
