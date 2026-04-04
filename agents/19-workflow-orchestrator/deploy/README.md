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

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `CHECKPOINT_STORE_CREDENTIALS` | Read/write `WORKFLOW_CHECKPOINT_REF` |
| `EXECUTOR_CREDENTIALS` | Authenticate to `WORKFLOW_EXECUTOR_REF` |
| `MODEL_API_KEY` | Planner `MODEL_API_ENDPOINT` |
| `WORKFLOW_AUDIT_CREDENTIALS` | Optional write to `WORKFLOW_AUDIT_REF` |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Orchestrator | 500m | 4 | 512Mi | 2Gi |

Large DAG definitions in planner context can spike memory; cap nodes per graph and externalize blob outputs.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when checkpoint R/W + executor heartbeat + DAG registry reachable |

Optional sub-check: `HEAD` on a well-known checkpoint key to detect permission regressions early.
