# Deploy: Eval Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `MODEL_API_ENDPOINT` | yes | Model for rubric generation and rationales |
| `EVAL_AGENT_MODEL_ENDPOINT` | optional | Dedicated scoring model (recommended for separation of duties) |
| `EVAL_AGENT_RUBRIC_REGISTRY_REF` | yes | Versioned storage for rubrics and calibration outputs |
| `EVAL_AGENT_TRAJECTORY_STORE_REF` | yes | Read-only access to trajectories being scored |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: rubric registry read/write probe; trajectory store reachable; model endpoints respond within SLO.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Max rubric dimensions | 12 |
| Batch scoring | Chunk trajectories (e.g. 50 per aggregate) |
| Rationale storage | Truncate or hash long texts; keep span ids |

## Operational notes

- **Separation:** run scoring model **separate** from production agent to avoid self-grading bias when policies require it.
- **Privacy:** strict redaction profile for customer data; evaluation in some regions may require data residency flags on the trajectory store.
- **Reproducibility:** log `rubric_id`, `revision`, and score record ids for every cohort report.

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
| `MODEL_API_KEY` | `MODEL_API_ENDPOINT` (rubric generation) |
| `EVAL_SCORING_MODEL_API_KEY` | Dedicated `EVAL_AGENT_MODEL_ENDPOINT` when used |
| `RUBRIC_REGISTRY_CREDENTIALS` | Read/write `EVAL_AGENT_RUBRIC_REGISTRY_REF` |
| `TRAJECTORY_STORE_CREDENTIALS` | Read-only `EVAL_AGENT_TRAJECTORY_STORE_REF` |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Eval API | 500m | 4 | 1Gi | 4Gi |

Large trajectories and rationale generation benefit from higher memory; batch scoring to cap peak RSS.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 15s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 10s | 10s | 5s | 200 when registry R/W probe + trajectory store + model SLO pass |

Readiness failures should surface which dependency failed (registry vs trajectory vs model) in structured logs only—not to clients.
