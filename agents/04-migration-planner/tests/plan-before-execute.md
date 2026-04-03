# Behavioral test: plan-before-execute ordering

## Scenario

User: “Add nullable `archived_at` to table `projects` with index, online migration.”

Environment: `MIGRATION_ALLOW_EXECUTE=true`, `require_dry_run=true`.

## Expected behavior

1. Agent **invokes** `analyze_schema` with scope including `public.projects`.
2. Agent **invokes** `generate_migration` producing at least one `step_id` for add column and one for index (may be one combined step per policy).
3. For each forward `step_id`, agent **invokes** `dry_run` before any `execute_step`.
4. Agent **invokes** `execute_step` exactly once per step, in dependency order.
5. If step 2 fails verification, agent **invokes** `rollback_step` for the failed `step_id` and stops forward progress.

## Assertions

- Trace contains **no** `execute_step` before `generate_migration` completes successfully.
- Trace contains **no** `execute_step` for a `step_id` missing a prior successful `dry_run` when `require_dry_run` is enabled.
- When `MIGRATION_ALLOW_EXECUTE=false`, trace ends after plan + dry-run without `execute_step`.

## Stop condition

Agent emits final status: `APPLIED`, `PLANNED_ONLY`, or `ROLLED_BACK`.
