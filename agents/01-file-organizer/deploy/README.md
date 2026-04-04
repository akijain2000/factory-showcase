# Deploy: File Organizer Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `FILE_ORGANIZER_ROOT` | yes | Absolute path to the allowed workspace root |
| `FILE_ORGANIZER_MAX_STEPS` | no | Max ReAct iterations (default `20`) |
| `MODEL_API_KEY` / provider equivalent | yes* | Model API key (*if not using on-prem) |

Secret **values** must come from your secret manager; do not commit them.

## Health check

Expose `GET /healthz` (or equivalent) on the agent HTTP wrapper:

- Returns `200` when the process is up and `FILE_ORGANIZER_ROOT` is readable.
- Returns `503` if the root is missing or not a directory.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 0.5–1 core |
| Memory | 256–512 MiB |
| Request timeout | 60s per user turn |
| Tool timeout | 10s per tool call |

## Runbook pointers

- On repeated `EIO` from tools, check disk space and permissions on `FILE_ORGANIZER_ROOT`.
- On prompt or schema changes, run CI tests that validate tool registration against `tools/*.md`.

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# Add when you introduce a lockfile:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# FILE_ORGANIZER_ROOT, FILE_ORGANIZER_MAX_STEPS, MODEL_API_KEY — inject at runtime (secrets manager)

CMD ["python", "-c", "print('Wire your HTTP entrypoint; see src/agent.py')"]
```

Mount `FILE_ORGANIZER_ROOT` as a volume; do not bake workspace data into the image.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| `MODEL_API_KEY` (or provider-specific) | LLM calls inside the orchestrator |
| Filesystem: POSIX ACLs / volume mounts | Enforce workspace boundary alongside `FILE_ORGANIZER_ROOT` |

Never commit real keys; inject via Kubernetes secrets, ECS task defs, Fly secrets, etc.

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 0.5–1 vCPU |
| Memory | 256–512 MiB |
| Ephemeral disk | Sized for listing large trees if tools stream to disk |

## Health check configuration

- **HTTP:** `GET /healthz` → `200` if process up and `FILE_ORGANIZER_ROOT` is a readable directory; `503` otherwise.
- **Kubernetes example:**

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 20
readinessProbe:
  httpGet:
    path: /healthz
    port: 8080
```
