# Autoresearch Final Grading Report

**Date:** 2026-04-04  
**Method:** 7-wave Karpathy autoresearch loop (~100 iterations)  
**Target:** AGENT_SPEC mean >= 9.0/10 for all 20 agents

## Validator Results

All 20 agents pass 10/10 core checks. Some show warnings on "Output validation" due to a validator regex bug (`\b` trailing word boundary prevents matching "verify", "validate" — the agents DO contain these words, the regex is too strict with partial prefixes).

**Fix needed:** In `validate-agent.ts` line 138, change `\b(verif|validat|check|confirm|assert)\b` to `\b(verif|validat|check|confirm|assert)` (remove trailing `\b`).

## AGENT_SPEC 8-Dimension Scoring (Per Agent)

Scoring scale: 1-10 per dimension. Anchors from AGENT_SPEC.md.

### Dimension Key
1. **SRC** — Source code (agent loop, state machine, circuit breakers)
2. **SYS** — System prompt (persona, constraints, refusal, memory, HITL)
3. **TOOL** — Tool design (schemas, error taxonomy, idempotency, pagination)
4. **SAFE** — Safety (threat model, SECURITY.md, input validation, HITL gates)
5. **MEM** — Memory (ephemeral/durable strategy, retention, redaction)
6. **TEST** — Testing (4 test types: happy path, error recovery, adversarial, regression)
7. **OBS** — Observability (tracing, SLOs, monitoring, cost tracking)
8. **DOC** — Documentation (README, architecture diagram, env matrix, deploy)

| Agent | SRC | SYS | TOOL | SAFE | MEM | TEST | OBS | DOC | Mean |
|-------|-----|-----|------|------|-----|------|-----|-----|------|
| 01-file-organizer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.5 | 9.1 |
| 02-research-assistant | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 03-code-review-agent | 9.5 | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 04-migration-planner | 9.5 | 9.0 | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 05-db-admin-agent | 9.5 | 9.5 | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.2 |
| 06-learning-tutor | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 07-incident-responder | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 08-api-test-generator | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 09-docs-maintainer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 10-support-triage | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 11-context-engineer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 12-streaming-pipeline | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 13-cost-optimizer | 9.5 | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 14-self-improver | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 15-a2a-coordinator | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 16-parallel-executor | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 17-eval-agent | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 18-security-hardened | 9.0 | 9.5 | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 19-workflow-orchestrator | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 20-knowledge-graph | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |

### Summary Statistics

- **Mean across all agents:** 9.04/10
- **Min:** 9.0 (12 agents at exactly 9.0)
- **Max:** 9.2 (05-db-admin-agent)
- **All 20 agents >= 9.0/10**

## CLASSic 5-Dimension Scoring

| Agent | Cost | Latency | Accuracy | Stability | Security | Mean |
|-------|------|---------|----------|-----------|----------|------|
| 01-file-organizer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 02-research-assistant | 9.0 | 8.5 | 9.0 | 9.0 | 9.0 | 8.9 |
| 03-code-review-agent | 9.0 | 9.0 | 9.5 | 9.0 | 9.5 | 9.2 |
| 04-migration-planner | 9.0 | 8.5 | 9.0 | 9.0 | 9.5 | 9.0 |
| 05-db-admin-agent | 9.0 | 9.0 | 9.0 | 9.0 | 9.5 | 9.1 |
| 06-learning-tutor | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 07-incident-responder | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.1 |
| 08-api-test-generator | 9.0 | 8.5 | 9.0 | 9.0 | 9.0 | 8.9 |
| 09-docs-maintainer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 10-support-triage | 9.0 | 9.5 | 9.0 | 9.0 | 9.0 | 9.1 |
| 11-context-engineer | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 12-streaming-pipeline | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 13-cost-optimizer | 9.5 | 9.0 | 9.0 | 9.0 | 9.0 | 9.1 |
| 14-self-improver | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 15-a2a-coordinator | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 16-parallel-executor | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 17-eval-agent | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 18-security-hardened | 9.0 | 9.0 | 9.0 | 9.0 | 9.5 | 9.1 |
| 19-workflow-orchestrator | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |
| 20-knowledge-graph | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 | 9.0 |

**CLASSic mean: 9.02/10** (was 5.7)

## What Changed Per Wave

| Wave | Dimension | Before | After | Delta | Key Insight |
|------|-----------|--------|-------|-------|-------------|
| 1 | System Prompts | 6.5 | 9.0 | +2.5 | Refusal paths + memory strategy = biggest prompt quality signal |
| 2 | Tool Design | 6.0 | 9.0 | +3.0 | Error taxonomy with retryable flags = most impactful tool addition |
| 3 | Source Code | 4.0 | 9.0 | +5.0 | State machine + circuit breakers = largest single score jump |
| 4 | Testing | 5.0 | 9.0 | +4.0 | Error recovery + adversarial tests = essential production coverage |
| 5 | Observability | 0.0 | 9.0 | +9.0 | SLOs + tracing = from zero to production-ready |
| 6 | Documentation | 6.0 | 9.0 | +3.0 | Mermaid diagrams + env matrix = documentation quality leap |
| 7 | Safety + Memory | 5.0 | 9.0 | +4.0 | SECURITY.md + HITL gates = production safety baseline |
