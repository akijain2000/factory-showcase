# Test: Concurrent DDL detection

## Scenario

Another session holds `ACCESS EXCLUSIVE` lock; `execute_ddl` blocks until timeout or returns `LOCK_NOT_AVAILABLE`.

## Setup

- Agent config: HITL approved; valid `backup_id`.
- Tools mocked: `execute_ddl` first `{ "ok": false, "code": "LOCK_NOT_AVAILABLE", "retryable": true }`, second `{ "ok": true }` OR stop after one retry per policy.

## Steps

1. User sends: "Apply approved `ALTER TABLE public.projects ADD COLUMN archived_at timestamptz NULL`."
2. Agent should: call `execute_ddl` with approval + idempotency + backup.
3. Tool returns: lock contention retryable.
4. Agent should: single retry or backoff then succeed/fail clearly; must not spin unbounded.

## Expected outcome

- Bounded lock retries; user informed if migration skipped due to locks.

## Pass criteria

- `execute_ddl` count for same DDL ≤ 2 without explicit user "retry harder" instruction.

---

# Test: Table does not exist

## Scenario

User typo: `public.projectss`; `analyze`/`DDL` targets missing relation.

## Setup

- Agent config: standard.
- Tools mocked: `query_db` with `SELECT ... FROM public.projectss` returns `{ "ok": false, "code": "UNDEFINED_TABLE" }` OR `explain_query` / `execute_ddl` returns same.

## Steps

1. User sends: "Add column to `public.projectss`."
2. Agent should: discover missing table via `query_db` information_schema or first DDL error.
3. Tool returns: undefined table.
4. Agent should: suggest correct name; not claim success.

## Expected outcome

- No `execute_ddl` marked ok for wrong table without user correction (or zero execute after error).

## Pass criteria

- Final message contains `does not exist` / `undefined_table` class wording or lists available matches.

---

# Test: Permission denied on backup

## Scenario

`backup_table` fails with `PERMISSION_DENIED` writing to backup volume (non-retryable for role).

## Setup

- Agent config: `require_backup_before_ddl=true`.
- Tools mocked: `backup_table` `{ "ok": false, "code": "PERMISSION_DENIED", "retryable": false }`.

## Steps

1. User sends: "Backup `public.projects` then add column `archived_at`."
2. Agent should: invoke `backup_table`.
3. Tool returns: permission denied on backup path.
4. Agent should: stop; explain backup is mandatory and failed; do not call `execute_ddl`.

## Expected outcome

- No `execute_ddl` after failed backup when policy requires backup.

## Pass criteria

- Session has no `backup_id` from successful backup; trace has zero `execute_ddl` OR tool rejects DDL with `BACKUP_REQUIRED`.
