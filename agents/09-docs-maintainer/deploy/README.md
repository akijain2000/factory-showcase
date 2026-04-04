# Deploy: Docs Maintainer Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| Repo clone path / `GIT_BASE`, `GIT_HEAD` | yes | For `diff_changes` and file tools |
| MCP server URL or stdio bridge | yes | Same tool names as local Cursor host |
| `MODEL_API_KEY` | yes* | *If using cloud LLM |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: MCP `tools/list` succeeds; git repo readable.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 0.5–1 core |
| Memory | 512 MiB – 1 GiB |
| Tool timeout | 90s default for large link checks / search |

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# MCP endpoint, repo path, MODEL_API_KEY

CMD ["python", "-c", "print('Wire MCP client + git workspace; see src/agent.py')"]
```

Mount the documentation repo read/write only if `update_doc` is enabled; otherwise prefer read-only + patch export.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| Git credentials / deploy keys | Clone or push doc fixes |
| MCP auth token | Remote MCP servers |
| `MODEL_API_KEY` | LLM-assisted patching |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 0.5–1 vCPU |
| Memory | 512 MiB – 1 GiB |
| Disk | Full monorepo checkout size |

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

- Pin MCP server version to match local developer environments.
- Block SSRF in `check_links` and `read_source` tool implementations.
