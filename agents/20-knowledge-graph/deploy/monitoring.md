# Monitoring: Knowledge Graph (20)

Entity extraction, relationship mapping, traversal, reasoning. Trace `traverse_graph` / `query_subgraph` as spans.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.5% | 30d | Graph API |
| Latency p50 / p95 | 200ms / 2s | 24h | Cached subgraph reads |
| Error rate | < 0.5% | 24h | 5xx + invalid graph ops |
| Cost per query | Baseline + alert | 7d | LLM extraction + embedding if used |
| **Traversal p99** | **< 30s** | 24h | Bounded hop query completion |
| **Entity resolution accuracy** | **> 90%** | 30d | Held-out labeled merge decisions |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| TraversalP99 | p99 ≥ 30s for 15m | high | Index health; hop limits; hot nodes |
| ERAccuracyLow | accuracy ≤ 88% rolling | critical | Retrain/retune `extract_entities`; review merges |
| GraphWriteLag | replication lag high | page | Store cluster |
| ReasoningDepthExceeded | rate of depth caps hit | medium | Query patterns; abuse |
| ExtractionFailures | spike in failed extracts | high | Upstream text quality |

## Dashboard spec

- **Row 1:** Queries/sec, traversals/sec, cache hit rate.
- **Row 2:** p50/p95/p99 traversal time; nodes/edges touched distribution.
- **Row 3:** Entity resolution precision/recall (sampled); conflict queue depth.
- **Breakdowns:** Graph partition, tenant, query pattern class.

## Health check endpoint spec

- **GET `/healthz`:** API up.
- **GET `/readyz`:** graph store reachable; can run lightweight `MATCH (n) RETURN count(n) LIMIT 1` equivalent.
- **GET `/graph/stats`:** node/edge counts (cached) for capacity planning.

## Runbook references

- `deploy/README.md`
- `tests/extract-traverse-reason-path.md`
- `tests/test-error-recovery.md`
