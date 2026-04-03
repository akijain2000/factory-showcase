---
name: s04-migration-planning
description: Maps dependencies, sequences dry-runs, and defines rollback steps for schema or package moves. Use when upgrades touch shared libraries, databases, or the migration-planner agent is invoked.
---

# Migration planning with dry-run and rollback

## Goal / overview

Plan a change so it can be rehearsed safely and reversed if signals go wrong. Pairs with agent `04-migration-planner`.

## When to use

- A dependency or schema version bump affects more than one service.
- Data backfills or DDL run in production windows.
- Rollback must be possible without manual heroics.

## Steps

1. Build a dependency graph: direct importers, runtime vs build-time edges, shared configuration, and data consumers.
2. Classify migration steps as **expand**, **dual-write**, **backfill**, **cutover**, **contract** (or the closest equivalent for the stack).
3. For each step, define prerequisites, success signals, and maximum blast radius (rows touched, downtime seconds).
4. Schedule dry-runs in a production-like environment: replay traffic samples or run migration scripts with `--dry-run` / transaction rollback.
5. Author rollback: inverse DDL or restore-from-snapshot, feature-flag revert, or pinned dependency rollback with ordering constraints.
6. Document a go/no-go checklist tied to metrics (error rate, queue depth, replication lag).

## Output format

- **Dependency summary**: diagram or bullet tree of affected components.
- **Step script**: ordered numbered steps with dry-run command, prod command, validation query, rollback pointer.
- **Risk register**: top five failure modes with detection and response.

## Gotchas

- Irreversible DDL (drop column) needs an expand/contract pair or backup proof before cutover.
- ORM caches and read replicas may lag; validate on replicas used by real traffic.
- Package lockfiles and container images must move in lockstep to avoid runtime mismatch.

## Test scenarios

1. **Shared library bump**: Ten services import a logging library; plan should order releases, name compatibility tests, and define rollback via version pin.
2. **Additive schema change**: New nullable column with backfill; plan should separate deploy of code that tolerates null from backfill job and final constraint.
3. **Failed dry-run**: Dry-run reports row count mismatch; plan should block production execution and list diagnostics before retry.
