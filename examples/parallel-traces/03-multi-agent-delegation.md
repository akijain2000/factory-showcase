# Parallel Trace: Multi-Agent Delegation with Conflict Resolution

Worked example showing how agent 15-a2a-coordinator discovers peer agents, delegates subtasks in parallel, and resolves conflicting results.

## Scenario

A product launch review task requiring security audit, performance review, and documentation check. Three specialist agents are available. The security and performance agents disagree on a caching recommendation.

## Trace

```
trace_id: tr-a2a-launch-001
task: "Pre-launch review for checkout-service v2.4"

[T+0ms] discover_agents
  input: { capability_tags: ["security-audit", "performance-review", "documentation-check"] }
  output: {
    agents: [
      { id: "agent-sec-01",  capabilities: ["security-audit", "dependency-scan"], protocol: "a2a-v1", status: "available" },
      { id: "agent-perf-02", capabilities: ["performance-review", "load-testing"], protocol: "a2a-v1", status: "available" },
      { id: "agent-docs-03", capabilities: ["documentation-check", "api-docs"], protocol: "a2a-v1", status: "available" }
    ]
  }

[T+100ms] negotiate_protocol
  input: {
    agents: ["agent-sec-01", "agent-perf-02", "agent-docs-03"],
    required_protocol: "a2a-v1",
    timeout_ms: 5000
  }
  output: {
    agreements: [
      { agent: "agent-sec-01",  protocol: "a2a-v1", response_format: "structured-json" },
      { agent: "agent-perf-02", protocol: "a2a-v1", response_format: "structured-json" },
      { agent: "agent-docs-03", protocol: "a2a-v1", response_format: "structured-json" }
    ],
    all_agreed: true
  }

--- PARALLEL DELEGATION ---

[T+200ms] delegate_task (parallel x3)
  to: agent-sec-01
  input: { task: "Security audit of checkout-service v2.4", scope: "dependencies, auth flows, data handling", deadline_ms: 30000 }

  to: agent-perf-02
  input: { task: "Performance review of checkout-service v2.4", scope: "response times, caching, resource usage", deadline_ms: 30000 }

  to: agent-docs-03
  input: { task: "Documentation check for checkout-service v2.4", scope: "API docs, deployment guide, changelog", deadline_ms: 30000 }

[T+8500ms] agent-docs-03 COMPLETED
  result: { status: "pass", findings: 2, severity: "low", details: ["Missing rate-limit docs", "Stale env var in deployment guide"] }

[T+15200ms] agent-sec-01 COMPLETED
  result: {
    status: "pass_with_warnings",
    findings: 3,
    severity: "medium",
    details: ["Cached auth tokens should have max-age 300s", "Add CSRF token to checkout form", "Pin dependency lodash to 4.17.21+"],
    recommendation: { caching: "reduce_ttl", reason: "auth token cached too long" }
  }

[T+22000ms] agent-perf-02 COMPLETED
  result: {
    status: "pass",
    findings: 1,
    severity: "info",
    details: ["P95 response time 340ms within SLO"],
    recommendation: { caching: "increase_ttl", reason: "cache hit ratio 62%, target 80%+" }
  }

[T+22100ms] collect_results
  input: { task_id: "tr-a2a-launch-001", agents: ["agent-sec-01", "agent-perf-02", "agent-docs-03"] }
  output: {
    all_complete: true,
    total_findings: 6,
    conflicts: [
      { dimension: "caching", agent_a: "agent-sec-01", position: "reduce_ttl", agent_b: "agent-perf-02", position: "increase_ttl" }
    ]
  }

[T+22200ms] resolve_conflicts
  input: {
    conflicts: [{ dimension: "caching", positions: ["reduce_ttl (security)", "increase_ttl (performance)"] }],
    resolution_strategy: "safety_first"
  }
  output: {
    resolution: "reduce_ttl",
    rationale: "Safety-first policy: security concerns about auth token caching take precedence over cache hit ratio optimization. Recommend reducing auth token TTL to 300s while increasing static asset cache TTL separately to improve hit ratio.",
    compromise: "Split caching policy: auth tokens 300s (security), static assets 3600s (performance)"
  }
```

## Key Patterns Demonstrated

1. **Capability-based discovery**: Finds agents by what they can do, not by name
2. **Protocol negotiation before delegation**: All agents agree on response format
3. **Parallel delegation with independent deadlines**: Each agent works concurrently
4. **Conflict detection**: Automated detection of contradictory recommendations
5. **Safety-first resolution**: When security and performance conflict, security wins with a documented compromise
