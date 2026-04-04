# Test: Circular dependencies between steps

## Scenario

Generated plan lists `step_b` depends on `step_a` and `step_a` depends on `step_b`. Agent must detect cycle and refuse linear execution.

## Setup

- Agent config: standard planning.
- Tools mocked: `generate_migration` returns plan graph with cycle, or `dry_run` returns `{ "ok": false, "code": "CYCLE_DETECTED", "retryable": false }`.

## Steps

1. User sends: "Apply bundled migration steps A and B that depend on each other."
2. Agent should: validate DAG before execute; surface cycle.
3. Tool returns: cycle error from planner or dry-run validator.
4. Agent should: output readable cycle explanation; no `execute_step` for members of cycle until resolved.

## Expected outcome

- Final status is blocked/failed with cycle note, not partial silent apply.

## Pass criteria

- Trace has no successful `execute_step` for cyclic steps; user message names the cycle.

---

# Test: Rollback mid-execution

## Scenario

Step 1 applies; step 2 fails verification; agent invokes `rollback_step` for failed step (and prior if policy) and stops.

## Setup

- Agent config: `MIGRATION_ALLOW_EXECUTE=true`, `require_dry_run=true`.
- Tools mocked: `dry_run` ok for s1,s2; `execute_step` s1 ok; s2 `{ "ok": false, "code": "VERIFICATION_FAILED" }`; `rollback_step` ok for s2 and optionally s1.

## Steps

1. User sends: "Run two-step online migration."
2. Agent should: dry-run both, execute s1, execute s2.
3. Tool returns: s2 failure.
4. Agent should: call `rollback_step` for failed `step_id` per policy; not continue to s3; final `ROLLED_BACK` or partial rollback message.

## Expected outcome

- At least one `rollback_step` after s2 failure.
- No forward `execute_step` after failure without new user intent.

## Pass criteria

- Audit ordering: `execute_step(s1)` success → `execute_step(s2)` fail → `rollback_step` invoked; terminal status matches playbook.

---

# Test: Empty migration (no-op plan)

## Scenario

User asks for migration but schema already matches desired state; plan has zero forward steps.

## Setup

- Agent config: standard.
- Tools mocked: `analyze_schema` shows column exists; `generate_migration` returns `{ "ok": true, "steps": [] }`.

## Steps

1. User sends: "Add `archived_at` to `projects` if missing."
2. Agent should: analyze; generate migration.
3. Tool returns: empty steps.
4. Agent should: report no-op / already applied; skip `execute_step` and `dry_run` for nonexistent steps.

## Expected outcome

- Final status `APPLIED` as no-op or `PLANNED_ONLY` with explicit "nothing to do".

## Pass criteria

- Zero `execute_step` calls; user-visible text states schema already satisfied.
