# Monitoring: Streaming Pipeline (12)

Event-driven pipeline with backpressure. Trace stream operations with `Span`; propagate context on `emit-event` / consumer boundaries via `inject_carrier`.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.9% | 30d | Sink + aggregator healthy |
| Latency p50 / p95 / p99 | 50ms / 200ms / 1s | 24h | Per-hop processing (not end-to-end backlog) |
| Error rate | < 0.5% | 24h | Failed emits + aggregate failures / events |
| Cost per million events | Baseline + 20% alert | 7d | Infra + optional LLM sidecars |
| **Throughput** | **> 1000 events/s** sustained | 15m min window | Per shard; sum for cluster |
| **Backpressure** | **< 10%** of intervals in “pressure” state | 1h | From `inspect_backpressure` / queue depth signals |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| ThroughputDrop | sustained < 800 evt/s for 10m | high | Check consumers; partition skew |
| BackpressureHigh | ≥ 10% pressure slots for 15m | critical | Scale consumers; inspect slow subscribers |
| EmitFailureBurst | emit error rate > 1% for 5m | page | Broker/auth; poison messages |
| LatencySLO | p99 > 1s per hop for 20m | medium | CPU; GC; network to sink |
| CostPerMillionSpike | > 1.2× baseline | medium | Review optional enrichment calls |

## Dashboard spec

- **Row 1:** Ingest RPS, egress RPS, shard lag, error rate.
- **Row 2:** Backpressure %, queue depth, cancel-subtree rate.
- **Row 3:** p50/p95/p99 per stage (`emit`, `aggregate`, `register_interceptor`).
- **Breakdowns:** By stream name, tenant, interceptor type.

## Health check endpoint spec

- **GET `/healthz`:** process up.
- **GET `/readyz`:** broker/cursor reachable; can publish test heartbeat topic.
- **GET `/metrics/stream` (optional):** last emit timestamp, consumer group lag snapshot.

Include `traceparent` on internal HTTP fan-out if any.

## Runbook references

- `deploy/README.md`
- `tests/test-error-recovery.md` — backpressure and cancellation
- `tools/inspect-backpressure.md`
