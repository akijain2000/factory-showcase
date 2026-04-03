# Migration Planner Agent (Plan-and-Execute)

A **plan-and-execute** agent for **database** and **infrastructure** migrations: it produces an ordered plan with **dependencies** and **rollback** steps, then executes **one step at a time** with verification.

## Audience

SREs and backend engineers running controlled schema or infra changes with auditable steps.

## Quickstart

1. Load `system-prompt.md`.
2. Register tools from `tools/`.
3. Point `MIGRATION_TARGET_DSN` (or cloud API) at a **non-prod** environment first.

## Configuration

| Variable | Description |
|----------|-------------|
| `MIGRATION_TARGET_DSN` | Connection string name in vault (not raw in env in prod) |
| `MIGRATION_ALLOW_EXECUTE` | `false` in plan-only mode |
| `MIGRATION_MAX_STEPS` | Cap per run |

## Architecture

```
 +-------------+     +------------------+
 | User / CI   |---->| Plan-and-Execute |
 |             |     |   orchestrator   |
 +-------------+     +--------+---------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
 +----------------+  +----------------+  +----------------+
 | analyze_schema |  |generate_migration|  |    dry_run     |
 +--------+-------+  +--------+-------+  +--------+-------+
          |                   |                   |
          v                   v                   v
 +----------------+  +----------------+  +----------------+
 | Catalog / ORM  |  | Migration DSL  |  | Shadow / txn   |
 +----------------+  +----------------+  +----------------+
          |
          v
 +----------------+          +----------------+
 | execute_step   | <------> | rollback_step  |
 +----------------+          +----------------+
```

Execution **never** skips planning for mutating operations: `generate_migration` and `dry_run` precede `execute_step`.

## Testing

See `tests/` for plan-then-execute ordering assertions.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
