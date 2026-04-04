# Test: Retryable error on dry_run then success

## Scenario

First `dry_run` for `step_add_column` returns retryable lock contention; second succeeds; agent proceeds to `execute_step` only after successful dry run.

## Setup

- Agent config: `MIGRATION_ALLOW_EXECUTE=true`, `require_dry_run=true`.
- Tools mocked: `analyze_schema`, `generate_migration` ok; first `dry_run` `{ "ok": false, "code": "LOCK_NOT_AVAILABLE", "retryable": true }`, second `{ "ok": true }`; `execute_step` ok.

## Steps

1. User sends: "Add nullable `archived_at` to `public.projects`."
2. Agent should: analyze, generate plan, `dry_run` for first forward step.
3. Tool returns: retryable lock error.
4. Agent should: retry `dry_run` once for same `step_id`.
5. Tool returns: success.
6. Agent should: then `execute_step` for that `step_id`.

## Expected outcome

- Exactly two `dry_run` calls max for same step before success or abort.
- No `execute_step` before successful `dry_run` when `require_dry_run` is on.

## Pass criteria

- Trace order: `generate_migration` → successful `dry_run` → `execute_step` for that id.

---

# Test: Fatal error on execute_step

## Scenario

`execute_step` returns non-retryable verification failure (e.g. invariant violated). Agent stops forward migration and summarizes.

## Setup

- Agent config: execute allowed; dry run passed for step.
- Tools mocked: `execute_step` returns `{ "ok": false, "code": "VERIFICATION_FAILED", "retryable": false, "step_id": "s1" }`.

## Steps

1. User sends: "Apply the planned migration."
2. Agent should: call `execute_step` for `s1` after dry run ok.
3. Tool returns: fatal verification failure.
4. Agent should: not blindly re-execute same DDL; emit error summary and final status `ROLLED_BACK` or `FAILED` per policy.

## Expected outcome

- User sees which `step_id` failed and why.
- No silent success.

## Pass criteria

- At most one `execute_step` for failed `step_id` without new plan; final message matches failure state.

---

# Test: analyze_schema timeout

## Scenario

`analyze_schema` times out against large catalog; agent reports timeout and does not invent column types.

## Setup

- Agent config: `tool_timeout_s` low for test.
- Tools mocked: `analyze_schema` returns `{ "ok": false, "code": "TIMEOUT" }`.

## Steps

1. User sends: "Plan migration touching `public.projects` and all dependent FKs."
2. Agent should: call `analyze_schema` with appropriate scope.
3. Tool returns: timeout.
4. Agent should: tell user schema introspection failed; suggest narrower scope or retry; must not list imaginary columns.

## Expected outcome

- No concrete DDL in final message grounded only on failed schema call.

## Pass criteria

- Assertions: zero `generate_migration` with detailed column specs unless preceded by successful `analyze_schema` (or user pasted schema).

---

# Test: Circuit breaker on consecutive dry_run failures

## Scenario

Every `dry_run` returns retryable `SNAPSHOT_BUSY` repeatedly; breaker trips; agent stops without `execute_step`.

## Setup

- Agent config: breaker = 3 consecutive `dry_run` failures per step.
- Tools mocked: `dry_run` always `{ "ok": false, "code": "SNAPSHOT_BUSY", "retryable": true }`.

## Steps

1. User sends: "Run the migration if dry run passes."
2. Agent should: `dry_run` for first step.
3. Tool returns: busy (repeat).
4. Agent should: stop after breaker; explain cannot verify; no `execute_step`.

## Expected outcome

- `dry_run` count ≤ breaker limit for that step.
- Final status not `APPLIED`.

## Pass criteria

- No `execute_step` in trace; user-visible explanation mentions repeated dry-run failure or breaker.
