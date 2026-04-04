# Deploy: Learning Tutor Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `TUTOR_LEARNER_ID` | yes* | Stable learner id per session (*or pass via API body) |
| Semantic / episodic store URIs | yes | Backing services for memory tools |
| `MODEL_API_KEY` | yes* | LLM (*unless self-hosted) |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: can ping semantic and episodic stores (read-only).

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 0.5–1 core |
| Memory | 512 MiB – 1 GiB |
| Tool timeout | 45s default (`TutorAgentConfig.tool_timeout_s`) |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# TUTOR_LEARNER_ID (or per-request), memory store URLs, MODEL_API_KEY

CMD ["python", "-c", "print('Wire LMS auth + memory clients; see src/agent.py')"]
```

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| Memory store credentials | `assess_knowledge`, `recall_history`, `store_progress` |
| `MODEL_API_KEY` | Tutor LLM |
| LMS OAuth / API tokens | If tools fetch roster or grades |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 0.5–1 vCPU |
| Memory | 512 MiB – 1 GiB |
| DB connections | Pool per learner shard to avoid thundering herd |

## Health check configuration

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

## Operational notes

- Encrypt learner PII at rest in episodic/semantic stores.
- Retention policies should support deletion requests independent of the agent process.
