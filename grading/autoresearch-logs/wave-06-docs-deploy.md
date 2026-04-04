# Wave 6: Documentation + Deploy — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 8 (Documentation) + Deploy infrastructure  
**Baseline:** Mean ~6.0/10 on documentation (basic READMEs, bare deploy/)

## What was done

Enriched all 20 agent READMEs with:
- Architecture diagrams (Mermaid flowcharts + state machine diagrams)
- Environment matrix tables (all env vars with required/default/description)
- Known limitations (3-5 honest, domain-specific limitations per agent)
- Security summaries (data flow, trust boundaries, PII handling)
- Rollback guides (undo procedures, audit log details, recovery steps)

Enriched all 20 deploy/README.md with:
- Dockerfile skeletons (FROM python:3.12-slim, proper layering)
- Required secrets lists
- Resource limits (CPU/memory recommendations)
- Health check configuration (Kubernetes probe specs)

## What INCREASES score (learnings)

1. **Mermaid architecture diagrams** — Visual documentation is the #1 quality signal for reviewers. A flowchart showing the agent's control flow is worth 1000 words. State machine diagrams showing IDLE→PLANNING→EXECUTING→DONE map directly to the code.
2. **Environment matrix** — A complete env var table prevents "works on my machine" failures. Every required secret and optional config should be listed with defaults.
3. **Known limitations** — Honest limitations build trust. "Thread-based timeouts don't cancel running tools" is honest. "No limitations" is suspicious.
4. **Rollback guide** — For production agents, knowing how to undo is as important as knowing how to do. The audit_log → LIFO reversal pattern is a concrete recovery procedure.
5. **Dockerfile with proper layering** — COPY requirements.txt first, then pip install, then COPY app. This enables Docker layer caching and faster rebuilds.
6. **Health check probes** — Kubernetes liveness/readiness probes with specific paths, delays, and timeouts enable automated recovery from unhealthy agents.

## What DECREASES score (anti-patterns found)

1. **README as marketing** — READMEs that only say "this agent is amazing" without architecture, limitations, or setup instructions score poorly.
2. **No deploy guidance** — Without Dockerfiles and health checks, agents can't be deployed. A bare deploy/README.md is a placeholder, not documentation.
3. **Missing env var docs** — Undocumented environment variables are the #1 cause of deployment failures. Every config value should be in the matrix.
4. **No security section** — Production agents handle user data. Without a security summary, reviewers assume the worst about data handling.
5. **Generic limitations** — "May have bugs" is not a limitation. "Cannot process files > 100MB due to memory constraints" is specific and actionable.

## Metrics after Wave 6

- 20/20 agents: architecture diagrams (Mermaid)
- 20/20 agents: environment matrix tables
- 20/20 agents: known limitations (3-5 per agent)
- 20/20 agents: security summaries
- 20/20 agents: rollback guides
- 20/20 agents: deploy/README.md with Dockerfiles and health checks
- Estimated dim 8 score: 9.0/10 (up from ~6.0)
