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

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# MIGRATION_TARGET_DSN, MIGRATION_ALLOW_EXECUTE, MODEL_API_KEY — from vault / CI secrets

CMD ["python", "-c", "print('Wire migration executor + HTTP; see src/agent.py')"]
```

Use a non-root user and network policies that only allow the migration target and metadata store.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| `MIGRATION_TARGET_DSN` | Database or control-plane credentials (vault reference) |
| `MIGRATION_ALLOW_EXECUTE` | Gate mutating steps (`true` only in approved pipelines) |
| `MODEL_API_KEY` | If LLM assists planning |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 1–2 vCPU (spikes during plan generation) |
| Memory | 512 MiB – 2 GiB depending on schema size |
| Wall clock | 30–120+ minutes for large plans — set job timeouts accordingly |

## Health check configuration

- `GET /healthz`: orchestrator process alive.
- `GET /readyz`: read-only connectivity to migration metadata and target.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
```
