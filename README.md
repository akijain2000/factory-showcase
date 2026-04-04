# Factory Showcase: 20 Skills + 20 Agents (Karpathy Loop + Autoresearch)

Testing and validating both [Skill Factory](https://github.com/akijain2000/skill-factory) and [Agent Factory](https://github.com/akijain2000/agent-factory) by producing real outputs, grading them with three evaluation frameworks, and feeding improvements back through 5 Karpathy-style cycles + a 7-wave autoresearch improvement loop (~100 iterations).

## Methodology: Adapted Karpathy Auto-Research Loop

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch): one editable surface, fixed metrics, continuous create-evaluate-keep/discard cycles.

```
Phase 1: Karpathy 5-Cycle Loop
  Cycle 1: CREATE      -- 10 new agents + 20 paired skills, baseline grading
  Cycle 2: CLASSic     -- Cost/Latency/Accuracy/Stability/Security evaluation
  Cycle 3: AdaRubric   -- Task-adaptive rubrics, domain-specific scoring
  Cycle 4: TRACES      -- Parallel reasoning traces, validator improvements
  Cycle 5: CONVERGE    -- Final re-grade, delta report

Phase 2: 7-Wave Autoresearch Loop (~100 iterations)
  Wave 1: PROMPTS     -- System prompt enrichment (refusal, memory, HITL, abstain)
  Wave 2: TOOLS       -- Error taxonomy, idempotency, pagination, timeouts
  Wave 3: SOURCE      -- Real agent loops, state machines, circuit breakers
  Wave 4: TESTS       -- 4 test types per agent (happy, error, adversarial, regression)
  Wave 5: OBSERVABILITY -- Tracing, SLOs, monitoring, cost tracking
  Wave 6: DOCS+DEPLOY -- Mermaid diagrams, env matrix, Dockerfiles, health checks
  Wave 7: SAFETY      -- SECURITY.md, HITL gates, memory strategy, threat models
```

## Results at a Glance

### Agents (AGENT_SPEC: 9.04/10)

```
AGENT_SPEC (8-dim):  Mean 9.04 / 10  (was 7.6 at Cycle 1, 7.8 at Cycle 5)
CLASSic (5-dim):     Mean 9.02 / 10  (was 5.5 at Cycle 1, 5.7 at Cycle 5)
Validator:           20/20 pass, 0 fail (10 checks each)
All 20 agents >= 9.0/10
Top agents:          05-db-admin (9.2), 03-code-review (9.1), 18-security-hardened (9.1)
```

### Skills (Mean: 9.1/10)

```
SKILL_SPEC:  Mean 9.1 / 10  (was 8.7 at Cycle 1)
Validator:   20/20 pass, 0 warnings (15 checks each)
All skills have test scenarios, examples, and gotchas sections
```

## Agents Overview (20)

| # | Agent | Architecture | Tools | AGENT_SPEC | CLASSic | Tests |
|---|-------|-------------|-------|------------|---------|-------|
| 1 | file-organizer | Minimal ReAct | 3 | 9.1 | 9.0 | 4 |
| 2 | research-assistant | ReAct + RAG | 5 | 9.0 | 8.9 | 4 |
| 3 | code-review-agent | Multi-agent supervisor | 7 | 9.1 | 9.2 | 4 |
| 4 | migration-planner | Plan-and-Execute | 6 | 9.1 | 9.0 | 4 |
| 5 | db-admin-agent | Safety-critical + HITL | 5 | 9.2 | 9.1 | 4 |
| 6 | learning-tutor | Memory-heavy | 4 | 9.0 | 9.0 | 4 |
| 7 | incident-responder | Autonomous loop | 5 | 9.0 | 9.1 | 4 |
| 8 | api-test-generator | Tool-heavy pipeline | 6 | 9.0 | 8.9 | 4 |
| 9 | docs-maintainer | MCP-forward | 5 | 9.0 | 9.0 | 4 |
| 10 | support-triage | Routing + classification | 5 | 9.0 | 9.1 | 4 |
| 11 | context-engineer | ACE context evolution | 5 | 9.0 | 9.0 | 4 |
| 12 | streaming-pipeline | Event-driven streaming | 5 | 9.0 | 9.0 | 4 |
| 13 | cost-optimizer | Budget-aware routing | 5 | 9.1 | 9.1 | 4 |
| 14 | self-improver | Karpathy harness | 5 | 9.0 | 9.0 | 4 |
| 15 | a2a-coordinator | Agent-to-Agent protocol | 5 | 9.0 | 9.0 | 4 |
| 16 | parallel-executor | Fan-out/fan-in concurrency | 5 | 9.1 | 9.0 | 4 |
| 17 | eval-agent | AdaRubric evaluator | 5 | 9.0 | 9.0 | 4 |
| 18 | security-hardened | Defense-in-depth | 5 | 9.1 | 9.1 | 4 |
| 19 | workflow-orchestrator | DAG engine | 5 | 9.1 | 9.0 | 4 |
| 20 | knowledge-graph | Entity + graph reasoning | 5 | 9.0 | 9.0 | 4 |

## Skills Overview (20 paired 1:1 with agents)

| # | Skill | Paired Agent | Overall |
|---|-------|-------------|---------|
| s01 | file-organization | 01-file-organizer | 9.0 |
| s02 | research-synthesis | 02-research-assistant | 9.2 |
| s03 | code-review-orchestration | 03-code-review-agent | 9.0 |
| s04 | migration-planning | 04-migration-planner | 9.2 |
| s05 | database-safety-gates | 05-db-admin-agent | 9.2 |
| s06 | adaptive-tutoring | 06-learning-tutor | 9.0 |
| s07 | incident-response-runbook | 07-incident-responder | 9.2 |
| s08 | api-test-generation | 08-api-test-generator | 9.2 |
| s09 | docs-sync-via-mcp | 09-docs-maintainer | 9.2 |
| s10 | support-routing | 10-support-triage | 9.0 |
| s11 | context-engineering | 11-context-engineer | 9.0 |
| s12 | streaming-event-design | 12-streaming-pipeline | 9.0 |
| s13 | cost-aware-model-routing | 13-cost-optimizer | 9.2 |
| s14 | self-improvement-harness | 14-self-improver | 9.2 |
| s15 | agent-to-agent-delegation | 15-a2a-coordinator | 9.0 |
| s16 | parallel-tool-execution | 16-parallel-executor | 9.0 |
| s17 | adaptive-evaluation | 17-eval-agent | 9.2 |
| s18 | prompt-injection-defense | 18-security-hardened | 9.0 |
| s19 | workflow-dag-design | 19-workflow-orchestrator | 9.2 |
| s20 | knowledge-graph-reasoning | 20-knowledge-graph | 9.0 |

## Directory Structure

```
factory-showcase/
├── README.md
├── improvements.md
├── scripts/
│   ├── classic-evaluator.md          # CLASSic 5-dim scoring template
│   └── adarubric-generator.md        # AdaRubric adaptive rubric generator
├── examples/
│   └── parallel-traces/              # 3 worked trace examples
│       ├── 01-fan-out-api-testing.md
│       ├── 02-dag-workflow-checkpoint.md
│       └── 03-multi-agent-delegation.md
├── skills/
│   ├── s01-file-organization/        ... s20-knowledge-graph-reasoning/
│   └── (20 skill directories, each with SKILL.md)
├── agents/
│   ├── 01-file-organizer/            ... 20-knowledge-graph/
│   └── (20 agent directories, each with README.md, system-prompt.md, tools/, tests/, src/, deploy/, SECURITY.md)
└── grading/
    ├── cycle-1-baseline.md           # Initial 8-dim + SKILL_SPEC grading
    ├── cycle-2-classic.md            # CLASSic 5-dim scoring + bottom 5 improvements
    ├── cycle-3-adarubric.md          # AdaRubric adaptive scoring + flagged fixes
    ├── cycle-4-combined.md           # Combined 3-framework re-evaluation
    ├── cycle-5-final.md              # Final convergence grading
    ├── delta-report.md               # Cycle 1 vs Cycle 5 comparison
    ├── autoresearch-final.md         # Autoresearch loop final grading (9.04/10)
    ├── autoresearch-delta.md         # Cycle 5 → Autoresearch delta report
    ├── autoresearch-logs/            # Per-wave learning logs (what increases/decreases scores)
    │   ├── wave-01-system-prompts.md
    │   ├── wave-02-tool-design.md
    │   ├── wave-03-source-code.md
    │   ├── wave-04-testing.md
    │   ├── wave-05-observability.md
    │   ├── wave-06-docs-deploy.md
    │   └── wave-07-safety-memory.md
    ├── skill-scores.md               # Original 10 skill grading (legacy)
    └── agent-scores.md               # Original 10 agent grading (legacy)
```

## Improvements Made to Both Factories

### Cycle 2: CLASSic Framework
- Added cost/budget awareness to 5 agents (system prompts)
- Identified that cost is the weakest operational dimension across all agents

### Cycle 3: AdaRubric
- Fixed 2 flagged dimensions (file-organizer undo safety, support-triage feedback loop)
- Improved 3 skills (api-test-generation, docs-sync, knowledge-graph-reasoning)

### Cycle 4: Validator Improvements
- **validate-agent.ts**: +2 checks (cost awareness, output validation)
- **validate-skill.ts**: +2 checks (example presence, gotchas section)

### Full Journey Delta (Cycle 1 → Autoresearch Final)

| Metric | Cycle 1 | Cycle 5 | Autoresearch Final | Total Change |
|--------|---------|---------|-------------------|--------------|
| Agent AGENT_SPEC mean | 7.6 | 7.8 | 9.04 | **+1.44** |
| Agent CLASSic mean | 5.5 | 5.7 | 9.02 | **+3.52** |
| Skill SKILL_SPEC mean | 8.7 | 9.1 | 9.1 | +0.4 |
| Tests per agent | 1 | 1 | 4 | **+3** |
| Files per agent | ~8 | ~8 | ~16 | **+8** |
| Agent validator | 8 checks | 10 checks | 10 checks | +25% |
| Regressions | -- | 0 | 0 | None |

See [autoresearch-delta.md](grading/autoresearch-delta.md) for the full autoresearch analysis, or [delta-report.md](grading/delta-report.md) for the original 5-cycle analysis.

### Per-Wave Learnings (What Increases/Decreases Scores)

Detailed learning logs from each autoresearch wave are in [`grading/autoresearch-logs/`](grading/autoresearch-logs/). Key findings:

- **Observability** was the biggest single-wave improvement (+9.0 from zero) -- SLOs and tracing are the most impactful additions for production readiness
- **Source code** had the second-largest jump (+5.0) -- replacing stubs with real state machines and circuit breakers
- **System prompts** benefited most from refusal paths and memory strategy sections (+2.5)
- **Anti-patterns** that decrease scores: copy-paste sections, missing error taxonomy, no circuit breakers, happy-path-only testing

## How to Run

### Validate a Skill
```bash
cd /path/to/skill-factory
bun scripts/validate-skill.ts /path/to/factory-showcase/skills/s01-file-organization/
```

### Validate an Agent
```bash
cd /path/to/agent-factory
bun scripts/validate-agent.ts /path/to/factory-showcase/agents/01-file-organizer/
```

### Score with CLASSic
See [scripts/classic-evaluator.md](scripts/classic-evaluator.md) for the scoring template.

### Score with AdaRubric
See [scripts/adarubric-generator.md](scripts/adarubric-generator.md) for adaptive rubric generation.

## Companion Projects

- [Skill Factory](https://github.com/akijain2000/skill-factory) -- LLM knowledge base for authoring AI agent skills
- [Agent Factory](https://github.com/akijain2000/agent-factory) -- LLM knowledge base for building production-quality AI agents
