# Cost Optimizer Agent (Budget-Aware)

An agent that optimizes **model routing**, **token accounting**, and **cost circuit breakers** for high-volume LLM workloads. It balances latency, capability, and spend using explicit budgets rather than implicit heuristics.

## Audience

FinOps-aware ML platform teams and application owners who need **predictable bills**, **graceful degradation**, and **auditable routing decisions**.

## Quickstart

1. Load `system-prompt.md`.
2. Wire tools to your usage ledger and router service.
3. Integrate `src/agent.py` patterns into your gateway’s pre-flight checks.

## Configuration

| Variable | Description |
|----------|-------------|
| `BUDGET_LEDGER_URI` | Storage for spend and token counters |
| `MODEL_ROUTE_TABLE_REF` | Config mapping tiers to model ids |
| `CIRCUIT_BREAKER_POLICY_REF` | Thresholds for halt / downgrade |
| `MODEL_API_ENDPOINT` | Gateway base URL for routed calls (no secrets in repo) |

## Architecture

```
                    +------------------+
                    | Incoming request |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | estimate_cost    |
                    | (preflight $ /   |
                    |  token envelope) |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | check_budget     |
                    | (tenant / team / |
                    |   project caps)  |
                    +--------+---------+
                             |
               +-------------+-------------+
               |                           |
         under budget                 over / hot
               |                           |
               v                           v
      +----------------+           +----------------+
      | route_to_model |           | downgrade_model|
      | (fast vs cap.) |           | or hard break  |
      +--------+-------+           +--------+-------+
               |                           |
               +-------------+-------------+
                             |
                             v
                    +------------------+
                    | track_tokens     |
                    | (actual usage +  |
                    |  attribution)    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Circuit breaker  |
                    | re-eval (async)  |
                    +------------------+
```

## Policies

- **Tiered routing:** cheap path for classification; capable path for codegen.
- **Attribution:** every `track_tokens` row links to `request_id` and cost center.
- **Breakers:** soft downgrade before hard stop unless policy says otherwise.

## Testing

See `tests/` for budget exhaustion and downgrade behavior.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
