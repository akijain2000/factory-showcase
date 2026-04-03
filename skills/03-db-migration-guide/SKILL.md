---
name: 03-db-migration-guide
description: Walks through safe database migration planning, execution, and verification using a written checklist. Use when applying schema or data migrations to shared or production databases.
---

# Database migration guide

## When to open the checklist

Use the linked checklist for any migration that changes schema, backfills data, rewrites large tables, or runs under traffic. Skip only for local disposable databases where rollback is irrelevant.

## Primary reference

Execute steps in order unless the database platform documentation explicitly allows parallel work:

- [references/checklist.md](references/checklist.md)

## How to use this skill

1. Read the checklist end-to-end once before writing migration code.
2. Copy the checklist into the change request or runbook, then tick items as they complete.
3. Keep a single owner for execution during the cutover window to avoid conflicting commands.
4. Record actual start/end times, connection targets (host and database name), and the exact migration revision or script IDs applied.

## Principles (short)

- **Reversibility** — Prefer migrations that remain compatible across deploy steps (expand → deploy → contract). Avoid destructive steps until backups and rollback paths are confirmed.
- **Locks and duration** — Large table rewrites can hold locks; plan low-traffic windows or online tooling supported by the engine.
- **Data backfills** — Batch work, throttle, and verify counts; avoid full-table scans without predicates when tables are large.
- **Secrets** — Never paste credentials into chat logs; use the project’s secret store or shell environment already configured on the runner.

## After completion

Archive the filled checklist with the release notes. If anything deviated from the plan, document the delta and whether follow-up migrations are required.
