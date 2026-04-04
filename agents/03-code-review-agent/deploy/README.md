# Deploy: Code Review Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `MODEL_API_KEY` | yes* | LLM provider key (*or on-prem equivalent) |
| `REVIEW_MAX_FILES` | no | Cap files per handoff (default `50`) |
| `REVIEW_SEVERITY_THRESHOLD` | no | `low` / `medium` / `high` for reporting filters |

Secrets must come from your vault; never embed in `system-prompt.md` or diffs.

## Health check

- `GET /healthz`: process up, can read `system-prompt.md` and register tools.
- `GET /readyz`: optional — subprocess linters / scanners on `PATH` if you shell out from tools.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 1–2 cores (parallel sub-reviewers in tool layer) |
| Memory | 512 MiB – 1 GiB for large diffs in memory |
| `tool_timeout_s` | 45s default in `CodeReviewConfig` — raise for huge repos |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# MODEL_API_KEY, optional paths to linters — inject at runtime

CMD ["python", "src/agent.py", "--help"]
```

Mount diffs or repos read-only; the container should not need write access except for temp artifacts.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| `MODEL_API_KEY` | Supervisor + sub-reviewer LLM calls |
| Optional static-analysis API keys | If tools call external SARIF or SAST services |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 1–2 vCPU |
| Memory | 512 MiB – 1 GiB |
| Ephemeral disk | For cloning large monorepos if tools require a working tree |

## Health check configuration

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
```

If you only run CLI batch jobs, replace HTTP probes with CI job success / exit code checks.

## Operational notes

- Truncate or chunk diffs that exceed model context before invoking `run`.
- Log model version and commit SHA with each review for auditability.
