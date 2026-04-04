# Deploy: API Test Generator Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| OpenAPI source path or URL | yes | Fed to `parse_openapi` implementation |
| Target API base URL / auth | yes* | For `run_test` (*mock-only mode may relax) |
| `MODEL_API_KEY` | yes* | *If generation is LLM-assisted |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: can read spec source and write workspace temp dir for artifacts.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 1–2 cores during `run_test` |
| Memory | 512 MiB – 2 GiB |
| Tool timeout | 300s default — align with slow integration suites |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt pytest requests

ENV PYTHONUNBUFFERED=1

# OPENAPI_SOURCE, API under test credentials, MODEL_API_KEY

CMD ["python", "-c", "print('Wire test runner + HTTP; see src/agent.py')"]
```

Use multi-stage builds to keep test dependencies out of minimal runtime images if you split generate vs run.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| API keys for target env | Authenticated `run_test` |
| `MODEL_API_KEY` | Spec-driven generation |
| CI token (optional) | Publishing generated tests back to repo |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 1–2 vCPU |
| Memory | 512 MiB – 2 GiB |
| Disk | Enough for generated suites + reports |

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

Batch CI jobs may use job success instead of HTTP probes.

## Operational notes

- Point `run_test` at staging by default; never at production without explicit approval.
- Scrub secrets from OpenAPI `example` values before committing generated tests.
