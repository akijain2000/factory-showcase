# Deploy: A2A Coordinator Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `AGENT_DIRECTORY_URI` | yes | Registry for `discover_agents` |
| `A2A_MESSAGE_BUS_REF` | yes | Bus or queue backing delegation |
| `POLICY_GATE_REF` | yes | Data classification and cross-trust rules |
| `MODEL_API_ENDPOINT` | yes | Coordinator reasoning (secrets via host) |
| `DELEGATE_TOKEN_ISSUER_REF` | recommended | Short-lived scoped credentials |

## Reliability

| Concern | Guidance |
|---------|----------|
| Timeouts | Set `per_handle_timeout_ms` conservatively; surface partials |
| Idempotency | Require `idempotency_key` for retried delegations |
| Backpressure | Limit concurrent subtasks per tenant |

## Security

- Enforce **mTLS** or **OAuth** peer authentication at the bus edge.
- Classify `inputs_ref` objects before enqueue; block `regulated` data to `public` tier agents.
- Log **handles** and **protocol_id**, not full payloads.

## Observability

- Metrics: `negotiation_fail_total`, `delegate_total`, `collect_timeout_total`, `conflict_total`, `resolution_strategy_total`.
- Tracing: propagate `correlation_id` from intake through each `task_handle`.

## Runbooks

- **Schema drift:** bump `payload_schema_ref` version; roll peers before coordinator promotion.
- **Conflict spikes:** temporarily switch default strategy to `human_escalation` for sensitive domains.

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "host_main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Required secrets

| Secret | Purpose |
|--------|---------|
| `AGENT_DIRECTORY_CREDENTIALS` | Registry access for `AGENT_DIRECTORY_URI` |
| `A2A_BUS_CREDENTIALS` | mTLS cert or OAuth for message bus |
| `DELEGATE_TOKEN_SIGNING_KEY` | Short-lived delegation JWTs if using `DELEGATE_TOKEN_ISSUER_REF` |
| `MODEL_API_KEY` | Coordinator reasoning |

## CPU and memory limits

| Workload | CPU request | CPU limit | Memory request | Memory limit |
|----------|-------------|-----------|----------------|--------------|
| Coordinator | 500m | 4 | 512Mi | 2Gi |

Spikes during fan-out; scale horizontally with sticky `correlation_id` routing if your bus supports it.

## Health check configuration

| Probe | Path / command | Initial delay | Period | Timeout | Success |
|-------|----------------|---------------|--------|---------|---------|
| Liveness | `GET /healthz` | 15s | 10s | 2s | HTTP 200 |
| Readiness | `GET /readyz` | 5s | 5s | 5s | 200 when directory + bus + policy gate probe pass |

Optional: readiness includes a lightweight `discover_agents` cache refresh success bit to avoid routing during registry outages.
