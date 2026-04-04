# Deploy: Security-Hardened Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `SECURITY_AGENT_POLICY_BUNDLE_REF` | yes | Signed policy location (rotation supported) |
| `SECURITY_AGENT_AUDIT_SINK_REF` | yes | Append-only audit destination |
| `MODEL_API_ENDPOINT` | yes | Inner model router |
| `SECURITY_AGENT_INJECTION_MODE` | optional | `fast_rules`, `hybrid`, or `full` default |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: policy bundle signature valid; audit sink append probe succeeds; schema registry for `validate_output` reachable.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Input size | Match `sanitize_input` max; reject early at edge |
| Audit throughput | Batch or async shipper to avoid blocking user path |
| Permission checks | Cache decisions 30–120s where safe (include scope in cache key) |

## Operational notes

- **Key material** for policy signing lives in KMS/HSM; never in environment variables.
- **Red team** regularly updates injection detectors; treat model-assisted signals as probabilistic.
- **Break-glass** roles must expire automatically and emit `severity: critical` audit events.

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
# Policy bundle verification uses KMS — mount via cloud SDK / sidecar
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `POLICY_BUNDLE_VERIFY_KEY` | KMS key id or JWKS URL for `SECURITY_AGENT_POLICY_BUNDLE_REF` |
| `AUDIT_SINK_CREDENTIALS` | Append to `SECURITY_AGENT_AUDIT_SINK_REF` |
| `MODEL_API_KEY` | Inner `MODEL_API_ENDPOINT` |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Security gateway | 500m | 4 | 512Mi | 2Gi |

`full` injection mode and large payloads increase CPU; async audit shipping reduces blocking but needs buffer memory.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 10s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when policy signature valid + audit append probe + output schema registry OK |

If readiness fails, **fail closed** for new sessions per policy; existing in-flight requests should drain or abort per your SLO.
