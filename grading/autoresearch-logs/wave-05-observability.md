# Wave 5: Observability — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 7 (Observability)  
**Baseline:** Mean 0.0/10 on this dimension (completely missing — no tracing, no SLOs, no monitoring)

## What was done

Added observability infrastructure to all 20 agents:
- src/tracing.py: OpenTelemetry-compatible tracing with span context, cost tracking decorator, structured log formatter
- deploy/monitoring.md: SLO definitions, alert rules, dashboard specs, health check endpoints, runbook references

## What INCREASES score (learnings)

1. **SLOs with specific numerical targets** — The most important addition. "The agent should be fast" is meaningless. "Latency p99 < 30s, error rate < 2%, availability 99.5%" is measurable and contractual.
2. **Domain-appropriate SLOs** — Incident responder needs p99 < 10s and 99.99% availability. File organizer can tolerate p99 < 30s. One-size-fits-all SLOs show no domain understanding.
3. **Cost tracking per request** — LLM agents have variable costs. Tracking cost_usd per request and alerting on anomalies prevents budget blow-ups.
4. **Trace context propagation** — W3C traceparent format enables distributed tracing across agent-to-agent calls. Without this, multi-agent systems are undebuggable.
5. **Health check endpoints** — Simple GET /health → 200 with status JSON enables load balancer health checks, k8s liveness probes, and monitoring dashboards.
6. **Alert rules with severities** — Not all alerts are equal. Error rate > 5% for 5 min is critical. Cost anomaly is warning. Runbook references tell on-call engineers what to do.

## What DECREASES score (anti-patterns found)

1. **Zero observability** — This was the baseline state. Without any tracing or monitoring, agents are black boxes in production. This was the single biggest gap across all 20 agents.
2. **Logs without trace IDs** — Plain text logs are unsearchable. Structured JSON logs with trace_id/span_id enable correlation across tool calls.
3. **No cost tracking** — LLM agents can silently spend hundreds of dollars. Without cost instrumentation, budget overruns are invisible.
4. **SLOs without alert rules** — Defining SLOs without alerts is aspirational, not operational. Each SLO needs a corresponding alert with severity and runbook.
5. **Missing health checks** — Without /health endpoints, orchestrators can't detect unhealthy agents. This causes cascading failures in multi-agent systems.

## Metrics after Wave 5

- 20/20 agents: src/tracing.py (all compile cleanly)
- 20/20 agents: deploy/monitoring.md with SLOs, alerts, dashboards, health checks
- Estimated dim 7 score: 8.5-9.0/10 (up from 0.0)

## Remaining gap to 9/10

- Wiring tracing into agent.py (import and instrument the run loop)
- Actual Grafana/Datadog dashboard JSON templates
- Cost alerting with budget enforcement (auto-pause on spend limit)
