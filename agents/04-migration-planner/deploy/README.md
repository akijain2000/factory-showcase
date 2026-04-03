# Deploy: Migration Planner Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `MIGRATION_TARGET_DSN` | yes | Secret reference to DB or API |
| `MIGRATION_ALLOW_EXECUTE` | yes | `true` only in approved pipelines |
| `MIGRATION_MAX_STEPS` | no | Per-run cap |
| `MIGRATION_REQUIRE_DRY_RUN` | no | Default `true` |

## Health check

- `GET /healthz`: orchestrator up.
- `GET /readyz`: can connect to migration metadata store and target (read-only ping).

## Resource limits

| Resource | Suggested |
|----------|-----------|
| DB statement timeout | Aligned with largest DDL expectation |
| Lock timeout | Explicit in executor |
| Agent wall time | 30–120 minutes for large plans |

## Runbook

- Failed `execute_step`: capture `migration_id`, consult rollback SQL, **invoke** `rollback_step` or manual runbook.
- Never disable dry-run in production without written exception.
