# Parallel Trace: DAG Workflow with Checkpoint Resume

Worked example showing how agent 19-workflow-orchestrator executes a migration DAG with conditional branching, survives a failure, checkpoints, and resumes.

## Scenario

A database migration workflow: validate schema, backup tables, apply DDL, run data migration, verify integrity. Steps 3 and 4 can run in parallel after backup completes.

## DAG Definition

```
[validate_schema] --> [backup_tables] --> [apply_ddl]
                                     --> [migrate_data]
                      [apply_ddl] -----> [verify_integrity]
                      [migrate_data] --> [verify_integrity]
```

## Trace

```
trace_id: tr-migration-dag-001
dag_id: dag-migration-v3

[T+0ms] define_dag
  input: {
    dag_id: "dag-migration-v3",
    steps: [
      { id: "validate_schema",   depends_on: [] },
      { id: "backup_tables",     depends_on: ["validate_schema"] },
      { id: "apply_ddl",         depends_on: ["backup_tables"] },
      { id: "migrate_data",      depends_on: ["backup_tables"] },
      { id: "verify_integrity",  depends_on: ["apply_ddl", "migrate_data"] }
    ]
  }
  output: { valid: true, topological_order: ["validate_schema", "backup_tables", ["apply_ddl", "migrate_data"], "verify_integrity"] }

[T+100ms] execute_step
  input: { step_id: "validate_schema", dag_id: "dag-migration-v3", inputs: { schema: "public" } }
  output: { status: "ok", result: { tables: 42, columns: 318, foreign_keys: 27 }, duration_ms: 850 }

[T+1000ms] execute_step
  input: { step_id: "backup_tables", dag_id: "dag-migration-v3", inputs: { tables: ["users", "orders", "products"] } }
  output: { status: "ok", result: { backup_id: "bk-20260403-001", size_mb: 1240 }, duration_ms: 45000 }

[T+46100ms] checkpoint_state
  input: { dag_id: "dag-migration-v3", completed: ["validate_schema", "backup_tables"] }
  output: { checkpoint_id: "ckpt-dag-v3-002", persisted: true }

--- PARALLEL WAVE: apply_ddl + migrate_data ---

[T+46200ms] execute_step (parallel)
  input: { step_id: "apply_ddl", dag_id: "dag-migration-v3", inputs: { ddl_file: "migration-v3.sql" } }
  output: { status: "ok", result: { statements_applied: 8 }, duration_ms: 3200 }

[T+46200ms] execute_step (parallel)
  input: { step_id: "migrate_data", dag_id: "dag-migration-v3", inputs: { batch_size: 10000 } }
  output: { status: "FAILED", error: "Connection reset after 12000 rows", duration_ms: 28000 }

--- FAILURE: migrate_data failed, checkpoint and resume ---

[T+74300ms] checkpoint_state
  input: { dag_id: "dag-migration-v3", completed: ["validate_schema", "backup_tables", "apply_ddl"], failed: ["migrate_data"] }
  output: { checkpoint_id: "ckpt-dag-v3-003", persisted: true }

--- OPERATOR FIXES CONNECTION, TRIGGERS RESUME ---

[T+180000ms] resume_from_checkpoint
  input: { checkpoint_id: "ckpt-dag-v3-003", dag_id: "dag-migration-v3" }
  output: { restored_state: { completed: ["validate_schema", "backup_tables", "apply_ddl"] }, pending_steps: ["migrate_data", "verify_integrity"] }

[T+180100ms] execute_step
  input: { step_id: "migrate_data", dag_id: "dag-migration-v3", inputs: { batch_size: 10000, resume_offset: 12000 } }
  output: { status: "ok", result: { rows_migrated: 48000, total: 60000 }, duration_ms: 35000 }

[T+215200ms] execute_step
  input: { step_id: "verify_integrity", dag_id: "dag-migration-v3", inputs: {} }
  output: { status: "ok", result: { checksum_match: true, row_count_match: true, fk_violations: 0 }, duration_ms: 12000 }
```

## Key Patterns Demonstrated

1. **Topological ordering**: DAG correctly identifies parallel wave (apply_ddl + migrate_data)
2. **Checkpoint before risky steps**: State saved after backup, before parallel wave
3. **Checkpoint on failure**: Failed state captured for later resume
4. **Resume with offset**: Data migration resumes from where it left off, not from scratch
5. **Join semantics**: verify_integrity waits for both apply_ddl AND migrate_data
