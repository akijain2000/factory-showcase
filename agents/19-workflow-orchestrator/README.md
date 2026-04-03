# Workflow Orchestrator Agent

A **DAG-backed workflow engine** for tool-using agents: explicit dependencies, **topological execution**, conditional branching, durable **checkpointing**, and **resume** after process restarts or partial failures.

## Audience

Automation engineers who outgrew linear chains and need predictable execution order, idempotent steps, and operational visibility into in-flight workflows.

## Quickstart

1. Load `system-prompt.md`.
2. Implement tools from `tools/` against your state store and worker queue.
3. Configure checkpoint storage via `WORKFLOW_CHECKPOINT_REF` (see `deploy/README.md`).
4. Run `tests/dag-branch-resume.md`.

## Configuration

| Variable | Description |
|----------|-------------|
| `WORKFLOW_CHECKPOINT_REF` | Durable key-value or object prefix for checkpoints |
| `WORKFLOW_EXECUTOR_REF` | Worker endpoint for `execute_step` |
| `MODEL_API_ENDPOINT` | Planner for DAG edits and condition expressions |

## Architecture

```
 +----------------+
 | DAG definition |
 +--------+-------+
          |
          v
 +-------------------+
 | Topological sort  |
 +---------+---------+
           |
           v
 +-------------------+
 | Step executor     |
 | (parallel layers) |
 +---------+---------+
           |
     +-----+-----+
     |           |
     v           v
+----------------+  +-------------------+
| Checkpoint mgr |  | Condition evaluator |
+--------+-------+  +---------+---------+
         |                    |
         +---------+----------+
                   |
                   v
         +-------------------+
         | Resume handler    |
         | (replay/skip ok)  |
         +-------------------+
```

## Execution semantics

- Steps are **idempotent** when `step_id` + `run_id` repeat.
- Checkpoints capture **outputs hash** and **branch taken** for each conditional edge.
- Resume replays **only** missing or failed steps unless `force` flags override policy.

## Testing

See `tests/dag-branch-resume.md`.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
