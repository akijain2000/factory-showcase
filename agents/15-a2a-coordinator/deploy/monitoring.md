# Monitoring: A2A Coordinator (15)

Multi-agent delegation and protocol negotiation. Propagate `traceparent` on outbound delegate calls.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Coordinator API |
| Latency p50 / p95 | 2s / 15s | 24h | Orchestration overhead only |
| Error rate | < 1% | 24h | Non-protocol failures |
| Cost per delegated task | Baseline + alert | 7d | Sum downstream + coordinator tokens |
| **Delegation latency p99** | **< 30s** | 24h | Submit delegate → first useful result |
| **Protocol error rate** | **< 2%** | 24h | Schema/version mismatch, timeout on handshake |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| DelegationP99 | p99 ≥ 30s for 20m | high | Slow workers; tighten timeouts |
| ProtocolErrors | ≥ 2% for 15m | critical | Run `protocol-mismatch` scenarios; version pins |
| ConflictRate | sustained elevate in `resolve_conflicts` | medium | Policy tuning |
| DiscoveryFailures | discover_agents failures > 1% | page | Registry/catalog |
| StallNoResults | collect_results timeouts | high | Partial result policy |

## Dashboard spec

- **Row 1:** Active delegations, tasks/hour, protocol errors %.
- **Row 2:** p50/p95/p99 delegation latency; retries per task.
- **Row 3:** Per-tool spans: `discover`, `negotiate`, `delegate`, `collect`, `resolve`.
- **Breakdowns:** Agent type, tenant, protocol version.

## Health check endpoint spec

- **GET `/healthz`:** coordinator up.
- **GET `/readyz`:** agent registry reachable; can list ≥1 peer in staging.
- **GET `/protocols`:** supported protocol versions (for probes).

## Runbook references

- `deploy/README.md`
- `tests/protocol-mismatch-and-conflict.md`
- `tests/test-error-recovery.md`
