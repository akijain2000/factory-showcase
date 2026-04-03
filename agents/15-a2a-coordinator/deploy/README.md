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
