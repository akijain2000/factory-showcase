# Deploy: Workflow Orchestrator Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `WORKFLOW_CHECKPOINT_REF` | yes | Durable storage for checkpoints |
| `WORKFLOW_EXECUTOR_REF` | yes | Worker fabric for `execute_step` |
| `MODEL_API_ENDPOINT` | yes | Planner for DAG authoring and repairs |
| `WORKFLOW_AUDIT_REF` | optional | Separate audit stream for branch decisions |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: checkpoint store read/write; executor heartbeat; DAG registry reachable.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Max nodes per DAG | 500 |
| Checkpoint frequency | After each side-effecting step or every N seconds for long tasks |
| Condition evaluation timeout | 50–200ms unless expressions are complex |

## Operational notes

- **Clock skew:** use logical clocks in `checkpoint_state` sequence, not wall time alone.
- **Migration:** bump `revision` instead of editing graphs for in-flight runs.
- **Observability:** alert on rising `retry_attempt` counts for the same `step_id`.
