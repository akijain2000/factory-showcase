# Database migration checklist

Use this list for relational databases under team or production load. Adapt naming to the migration framework in use (Liquibase, Flyway, Rails, Prisma, Alembic, etc.).

## Pre-migration

- [ ] **Change classification** — Schema-only, data backfill, index rebuild, or destructive drop/rename recorded in the ticket.
- [ ] **Risk note** — Estimated table sizes, lock expectations, and blast radius (single tenant vs global) written down.
- [ ] **Backup** — Fresh backup or snapshot taken; restore drill performed recently enough to trust the path.
- [ ] **Rollback story** — Down migration tested OR forward-only plan with feature flags / dual-write documented.
- [ ] **Compatibility window** — Application versions expected before, during, and after the migration listed; expand/contract steps ordered.
- [ ] **Replica lag** — If replicas exist, confirm lag thresholds and monitoring alerts for the maintenance window.
- [ ] **Access** — Credentials limited to least privilege; break-glass account availability confirmed if needed.
- [ ] **Dry run** — Migration executed against a copy with production-like volume or `EXPLAIN` reviewed for heavy statements.
- [ ] **Object inventory** — Tables, views, functions, triggers, and constraints touched are listed; dependent jobs noted.
- [ ] **Communication** — Stakeholders notified with start time, expected duration, and user-visible impact (if any).

## Migration authoring

- [ ] **Transactions** — Each step fits transaction boundaries supported by the engine; DDL splitting rules respected.
- [ ] **Idempotency** — Re-running failed steps does not corrupt data (guards with `IF NOT EXISTS`, existence checks, or sentinel values).
- [ ] **Defaults** — New `NOT NULL` columns either have defaults or are added in two phases (add nullable → backfill → enforce).
- [ ] **Indexes** — New indexes built `CONCURRENTLY` or equivalent when available; avoid blocking writes on large tables.
- [ ] **Foreign keys** — Added in the order that prevents validation scans from locking parent tables unexpectedly.
- [ ] **Data fixes** — Backfills chunked with commit boundaries; batch size tuned to keep replication healthy.
- [ ] **Permissions** — Grants and RLS policies updated in the same release as object changes.
- [ ] **Enum and check changes** — Enum label additions vs removals sequenced; widening vs narrowing check constraints tested against production-like data.
- [ ] **Generated columns** — Order of operations matches engine rules when adding stored generated columns referencing other columns.
- [ ] **Partitioning** — Attach/detach partition steps ordered; partition bounds validated so rows do not land in `DEFAULT` unexpectedly.
- [ ] **Views and materialized views** — Dependent views refreshed or recreated in the right phase; `REFRESH MATERIALIZED CONCURRENTLY` prerequisites met.

## Pre-execution (day-of)

- [ ] **Freeze** — Automated deploys that could race the schema change paused or coordinated.
- [ ] **Health baseline** — Error rates, saturation, and replication lag captured as baseline numbers.
- [ ] **Runbook open** — Exact commands, file paths, and version numbers ready in one place.
- [ ] **Owner** — Single operator named; secondary on-call aware.
- [ ] **Connectivity** — VPN or bastion access verified from the execution host.
- [ ] **Maintenance flags** — Feature flags or read-only modes flipped if the plan requires them.
- [ ] **Statement timeouts** — Session `statement_timeout` and lock timeout values set for the operator session vs application defaults.
- [ ] **Kill switch** — Criteria documented for aborting mid-migration (e.g. lock wait > N minutes) and who approves the abort.

## Execution

- [ ] **Target confirmation** — Database name and host triple-checked against the ticket (prod vs staging).
- [ ] **Migrations applied** — CLI output stored (stdout/stderr) with timestamps.
- [ ] **Lock watch** — Long-running queries monitored; prepared to pause or reschedule if contention spikes.
- [ ] **Mid-point validation** — Row counts or checksum spot checks after large backfills.
- [ ] **App deploy order** — Migrations and application binaries rolled out in the agreed sequence (migrate-first vs code-first).
- [ ] **Long DDL watch** — For engines that allow, progress monitored (`pg_stat_progress_*` or vendor equivalent) instead of assuming silence means success.
- [ ] **Binary log / logical replication** — If in use, confirm replication filters include new tables and no silent skip rules will strand subscribers.

## Post-migration

- [ ] **Schema verification** — `\d`, `information_schema`, or equivalent confirms expected columns, types, and indexes.
- [ ] **Application smoke** — Critical read/write paths exercised in staging; production canary if applicable.
- [ ] **Metrics** — Error rate, latency, replication lag compared to baseline; no new deadlocks or lock waits.
- [ ] **Vacuum/analyze** — Statistics refreshed if the engine requires it after bulk changes.
- [ ] **Cleanup** — Temporary tables or dual-write paths removed per the expand/contract schedule.
- [ ] **Documentation** — ER diagrams or internal wiki updated when public contracts changed.
- [ ] **Ticket closure** — Checklist attached, owners tagged, and follow-up tasks filed for any deferred work.
- [ ] **Backup retention** — Post-migration backup or snapshot labeled and retained per policy before old snapshots expire.
- [ ] **Slow query review** — Top queries after cutover compared to baseline; missing indexes from new access patterns filed as follow-ups.
- [ ] **Cost signals** — Storage growth and IOPS alarms checked if the migration added large indexes or wider rows.

## Incident triggers (stop and escalate)

- Unexpected lock timeouts or cascading replica lag.
- Application error spike correlated with migration timestamp.
- Mismatch between expected and actual row counts after a backfill.
- Failed migration mid-transaction without a clear resume path.

## Post-incident (if rollback or repair ran)

- [ ] Root cause and timeline documented.
- [ ] Data reconciliation queries saved with results.
- [ ] Follow-up migration hardens guards against repeat failure.
- [ ] **Peer review** — Second engineer reviewed the migration SQL and the order of operations before the retry window.

## Reference queries (adapt to engine)

- Row-count parity: snapshot counts for touched tables before vs after stored in the ticket.
- Integrity: foreign-key orphan checks run where the migration rewrites keys or partitions.
- Sequence alignment — For serial/identity columns after bulk imports, verify `max(id)` matches sequence `last_value` where applicable.
