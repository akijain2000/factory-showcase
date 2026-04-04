# Deploy: Context Engineer Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `CONTEXT_STORE_URI` | yes | Durable storage for bundles, reflections, and prompt metadata |
| `CONTEXT_MAX_TOKENS` | yes | Working context ceiling used by compression triggers |
| `PROMPT_VERSION_NAMESPACE` | yes | Isolated namespace for draft vs. production prompt revisions |
| `MODEL_API_ENDPOINT` | yes | Upstream inference endpoint for the agent’s own calls (credentials via host secret store) |
| `REDACTION_RULESET_REF` | recommended | Pointer to org redaction patterns for `curate_context` |

## Health and readiness

- **Liveness:** process responds within SLO; background summarization workers heartbeating.
- **Readiness:** `CONTEXT_STORE_URI` reachable; prompt registry readable; rate limits for reflection analytics not exceeded.

## Scaling

| Concern | Guidance |
|---------|----------|
| Bundle write amplification | Batch append reflections; avoid per-token writes |
| Compression cost | Offload to async worker tier; cap concurrent `compress_context` jobs per tenant |
| Prompt promotion | Single-writer per `PROMPT_VERSION_NAMESPACE`; use `expected_base_hash` |

## Security

- **Secrets:** supply credentials only through the host’s secret manager; never log full prompts if they contain customer data.
- **Integrity:** sign promoted prompt versions; reject `update_system_prompt` if review ticket is not in `approved` state.
- **Tenant isolation:** partition `bundle_id` and store keys by tenant id at the persistence layer.

## Observability

- Metrics: `curate_context_duration_ms`, `compression_ratio`, `quality_pass_rate`, `prompt_dry_run_count`, `prompt_promotion_count`.
- Tracing: propagate `session_id` and `bundle_id` on all tool spans.

## Dockerfile skeleton

```dockerfile
# Reference image — pin versions in production
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
# Load CONTEXT_STORE_URI, MODEL credentials from orchestrator — not baked in
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `MODEL_API_KEY` / OAuth client | Authenticate to `MODEL_API_ENDPOINT` |
| `CONTEXT_STORE_CREDENTIALS` | DB/object-store access for `CONTEXT_STORE_URI` |
| `PROMPT_SIGNING_KEY` (optional) | KMS reference for verifying promoted prompt signatures |

Never commit secrets; inject via your platform secret store (Kubernetes secrets, Vault, Parameter Store, etc.).

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| API + agent loop | 250m | 2 | 512Mi | 2Gi |
| Async compression worker | 500m | 4 | 1Gi | 4Gi |

Tune for `CONTEXT_MAX_TOKENS` and concurrent tenants; compression workers need headroom for large bundles.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 3s | 200 when store + registry reachable |

gRPC or custom runtimes: equivalent checks must verify `CONTEXT_STORE_URI` connectivity and prompt registry read access within SLO.
