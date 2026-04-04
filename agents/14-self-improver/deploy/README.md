# Deploy: Self-Improver Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `PROMPT_REGISTRY_URI` | yes | Versioned prompt storage with hash concurrency |
| `EVAL_SUITE_REF` | yes | Canonical suite manifest location |
| `METRICS_STORE_URI` | yes | Run summaries and comparison indexes |
| `EVAL_RUNNER_ENDPOINT` | yes | Sandboxed job executor for `run_evaluation` |
| `MODEL_API_ENDPOINT` | yes | Model access for eval worker (secrets via host) |

## Isolation

- Run evaluations in **network-restricted** sandboxes with fixture data only.
- Separate **production** registry namespace from **experiment** namespace.

## Quotas

| Resource | Suggested |
|----------|-----------|
| Concurrent evals | Small pool; queue overflow returns `RUNNER_BUSY` |
| Artifact retention | 30–90 days with lifecycle rules |
| Prompt diff size | Enforce max bytes; reject megabyte-scale churn |

## Governance

- Require `review_ticket_id` for `commit_or_revert: keep` in regulated environments.
- Maintain **rollback_handle** in CMDB; test rollback quarterly.

## Observability

- Metrics: `eval_run_duration_sec`, `gate_pass_rate`, `commit_rate`, `revert_rate`, `suite_version_skew_alerts`.
- Trace: link `run_id`, `candidate_id`, and `compare_report_id` across spans.

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
# Eval runner is usually a separate deployment — wire EVAL_RUNNER_ENDPOINT
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `PROMPT_REGISTRY_CREDENTIALS` | Read/write `PROMPT_REGISTRY_URI` |
| `METRICS_STORE_CREDENTIALS` | Write `METRICS_STORE_URI` |
| `EVAL_RUNNER_AUTH` | Call sandboxed `EVAL_RUNNER_ENDPOINT` |
| `MODEL_API_KEY` | Eval worker / harness model access |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Harness API | 250m | 2 | 512Mi | 2Gi |
| Eval worker pool | 2 | 8 | 4Gi | 16Gi |

Eval jobs dominate CPU/RAM; cap concurrent runs via queue depth and `RUNNER_BUSY` responses.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 20s | 15s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 10s | 10s | 5s | 200 when registry + metrics + runner handshake succeed |

Readiness should fail if experiment namespace can reach production registry paths (misconfiguration guard).
