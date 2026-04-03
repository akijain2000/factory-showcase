# Tools: Migration Planner Agent

| Tool | Phase | Purpose |
|------|-------|---------|
| `analyze_schema` | Plan | Inspect current schema / topology |
| `generate_migration` | Plan | Create forward + rollback artifacts |
| `dry_run` | Pre-exec | Validate step without committing |
| `execute_step` | Exec | Apply one forward step |
| `rollback_step` | Recovery | Apply rollback for a failed or reverted step |
