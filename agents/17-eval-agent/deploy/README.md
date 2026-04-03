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
