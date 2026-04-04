# Autoresearch Learnings: What Makes a 9/10 Agent

Compiled from 7 waves of autoresearch across 20 agents (~100 iterations).

## The Score Equation

An agent's AGENT_SPEC score is determined by 8 dimensions. Here is what each dimension needs to reach 9/10, ranked by impact on overall score:

### 1. Source Code (Impact: Very High)
**From 4.0 to 9.0 in one wave**

What gets you to 9:
- State machine with explicit enum states (IDLE, PLANNING, EXECUTING, WAITING_TOOL, ERROR, DONE)
- Transition table that prevents invalid state changes
- Circuit breakers: max_steps, max_wall_time_s, max_spend_usd
- Per-tool timeouts with cancellation handling
- Retryable vs fatal error dispatch
- Persistence hooks (save_state / load_state)
- Audit log tracking all mutations
- LLMClient as Protocol (not ABC) for testability

What kills the score:
- NotImplementedError stubs (instant 0/10)
- No state machine (vibes-based execution)
- No circuit breakers (runaway agents)
- Copy-paste loops (same code for all agents)

### 2. Observability (Impact: Very High)
**From 0.0 to 9.0 in one wave**

What gets you to 9:
- SLOs with specific numerical targets (latency p99 < Xs, error rate < Y%)
- Domain-appropriate thresholds (incident responder: p99 < 10s; file organizer: p99 < 30s)
- OpenTelemetry-compatible tracing with span context propagation
- Cost tracking per request (tokens + USD)
- Alert rules with severities and runbook pointers
- Health check endpoints (GET /health → 200 JSON)

What kills the score:
- Zero observability infrastructure (the baseline for all 20 agents)
- Logs without trace IDs
- SLOs without alert rules
- Generic thresholds for all agents

### 3. Testing (Impact: High)
**From 5.0 to 9.0 in one wave**

What gets you to 9:
- 4 test types: happy path, error recovery, adversarial, regression
- Structured format: Scenario/Setup/Steps/Expected/Pass criteria
- Tool mock alignment with error taxonomy codes
- Circuit breaker trigger tests
- Domain-specific regression cases
- Prompt injection adversarial tests

What kills the score:
- Happy path only (tells you nothing about failure behavior)
- No adversarial tests (no evidence constraints work)
- Generic error tests ("tool fails, agent handles it")
- Missing mock details (unreproducible tests)

### 4. Safety (Impact: High)
**From 6.0 to 9.0 in one wave**

What gets you to 9:
- SECURITY.md with domain-specific threat model
- HITL gates with timeout behavior
- Data classification tables
- Incident response playbook
- Memory redaction rules (never persist PII)
- Compliance references (GDPR, SOC2)

What kills the score:
- No security documentation
- HITL without timeout (agent hangs forever)
- No data classification
- Generic compliance notes

### 5. Tool Design (Impact: High)
**From 6.0 to 9.0 in one wave**

What gets you to 9:
- Error taxonomy with retryable flags per tool
- Per-tool timeouts and rate limits
- Idempotency keys for mutating tools
- Pagination for list/query tools
- Domain-specific error codes (not just HTTP)

What kills the score:
- No error documentation at all
- Idempotency on read-only tools (noise)
- Pagination on single-item tools (wrong)
- Timeout without backoff strategy

### 6. Documentation (Impact: Medium)
**From 6.0 to 9.0 in one wave**

What gets you to 9:
- Architecture Mermaid diagrams (flowchart + state machine)
- Environment variable matrix (complete)
- Known limitations (honest, domain-specific, with workarounds)
- Security summary in README
- Rollback guide with procedures
- Deploy README with Dockerfile, secrets, resource limits

What kills the score:
- Marketing-only README
- No deploy guidance
- Undocumented env vars
- "No limitations" claim

### 7. System Prompts (Impact: Medium)
**From 6.5 to 9.0 in one wave**

What gets you to 9:
- Version + changelog header
- Explicit refusal and escalation paths
- Memory strategy (ephemeral vs durable)
- Abstain rules (when NOT to call tools)
- Structured output format
- Cost awareness section
- HITL gates section

What kills the score:
- Copy-paste sections across agents
- No escalation path (agent tries forever)
- Missing cost awareness
- Tool name drift (prompt mentions non-existent tools)

### 8. Memory (Impact: Medium)
**From 4.0 to 9.0 across two waves**

What gets you to 9:
- Ephemeral vs durable state distinction
- Retention policy with specific durations
- Redaction rules for sensitive data
- Schema migration strategy
- Cross-version compatibility notes

What kills the score:
- No memory strategy at all
- Persisting PII without redaction
- No schema migration plan

## Universal Principles

1. **Domain specificity always beats generics.** A file organizer with path traversal threat modeling scores higher than one with generic "security is important."

2. **Numerical targets beat qualitative claims.** "Latency p99 < 30s" scores higher than "should be fast."

3. **Honest limitations build trust.** Agents that admit their weaknesses (thread-based timeouts can't cancel) score higher than those that claim perfection.

4. **Production artifacts matter.** Dockerfiles, health checks, and monitoring configs show the agent can be deployed, not just demonstrated.

5. **Testing negative paths is more valuable than testing happy paths.** Everyone can write a test where everything works. Testing what happens when everything breaks separates toys from production agents.

6. **The biggest wins come from dimensions that start at zero.** Observability went from 0 to 9 because adding ANY tracing infrastructure is transformative when there was none.
