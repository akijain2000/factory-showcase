# Factory Showcase: 20 Skills + 20 Agents (Karpathy Loop)

Testing and validating both [Skill Factory](https://github.com/akijain2000/skill-factory) and [Agent Factory](https://github.com/akijain2000/agent-factory) by producing real outputs, grading them with three evaluation frameworks, and feeding improvements back through 5 Karpathy-style auto-research cycles.

## Methodology: Adapted Karpathy Auto-Research Loop

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch): one editable surface, fixed metrics, continuous create-evaluate-keep/discard cycles.

```
Cycle 1: CREATE      -- 10 new agents + 20 paired skills, baseline grading
Cycle 2: CLASSic     -- Cost/Latency/Accuracy/Stability/Security evaluation, improve bottom 5
Cycle 3: AdaRubric   -- Task-adaptive rubrics, domain-specific scoring, fix flagged dims
Cycle 4: TRACES      -- Parallel reasoning traces, validator improvements, combined eval
Cycle 5: CONVERGE    -- Final re-grade, delta report, push improvements to all repos
```

## Results at a Glance

### Agents (Combined: 5.9/10 across 3 frameworks)

```
AGENT_SPEC (8-dim):  Mean 7.8 / 10  (was 7.6 at Cycle 1)
CLASSic (5-dim):     Mean 5.7 / 10  (was 5.5 at Cycle 1)
AdaRubric (5-dim):   Mean 3.7 / 5.0
Validator:           20/20 pass, 0 fail (10 checks each)
Top agents:          13-cost-optimizer (6.8), 16-parallel-executor (6.6), 18-security-hardened (6.6)
```

### Skills (Mean: 9.1/10)

```
SKILL_SPEC:  Mean 9.1 / 10  (was 8.7 at Cycle 1)
Validator:   20/20 pass, 0 warnings (15 checks each)
All skills have test scenarios, examples, and gotchas sections
```

## Agents Overview (20)

| # | Agent | Architecture | Tools | Combined | Pattern Era |
|---|-------|-------------|-------|----------|-------------|
| 1 | file-organizer | Minimal ReAct | 3 | 5.4 | Classic |
| 2 | research-assistant | ReAct + RAG | 5 | 5.8 | Classic |
| 3 | code-review-agent | Multi-agent supervisor | 7 | 5.7 | Classic |
| 4 | migration-planner | Plan-and-Execute | 6 | 5.9 | Classic |
| 5 | db-admin-agent | Safety-critical + HITL | 5 | 6.3 | Classic |
| 6 | learning-tutor | Memory-heavy | 4 | 5.5 | Classic |
| 7 | incident-responder | Autonomous loop | 5 | 6.3 | Classic |
| 8 | api-test-generator | Tool-heavy pipeline | 6 | 5.6 | Classic |
| 9 | docs-maintainer | MCP-forward | 5 | 5.4 | Classic |
| 10 | support-triage | Routing + classification | 5 | 5.6 | Classic |
| 11 | context-engineer | ACE context evolution | 5 | 5.9 | 2026 |
| 12 | streaming-pipeline | Event-driven streaming | 5 | 6.0 | 2026 |
| 13 | cost-optimizer | Budget-aware routing | 5 | 6.8 | 2026 |
| 14 | self-improver | Karpathy harness | 5 | 6.1 | 2026 |
| 15 | a2a-coordinator | Agent-to-Agent protocol | 5 | 6.0 | 2026 |
| 16 | parallel-executor | Fan-out/fan-in concurrency | 5 | 6.6 | 2026 |
| 17 | eval-agent | AdaRubric evaluator | 5 | 6.1 | 2026 |
| 18 | security-hardened | Defense-in-depth | 5 | 6.6 | 2026 |
| 19 | workflow-orchestrator | DAG engine | 5 | 6.0 | 2026 |
| 20 | knowledge-graph | Entity + graph reasoning | 5 | 5.7 | 2026 |

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
│   └── (20 agent directories, each with README.md, system-prompt.md, tools/, tests/, src/)
└── grading/
    ├── cycle-1-baseline.md           # Initial 8-dim + SKILL_SPEC grading
    ├── cycle-2-classic.md            # CLASSic 5-dim scoring + bottom 5 improvements
    ├── cycle-3-adarubric.md          # AdaRubric adaptive scoring + flagged fixes
    ├── cycle-4-combined.md           # Combined 3-framework re-evaluation
    ├── cycle-5-final.md              # Final convergence grading
    ├── delta-report.md               # Cycle 1 vs Cycle 5 comparison
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

### Karpathy Loop Delta

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Agent AGENT_SPEC mean | 7.6 | 7.8 | +0.2 |
| Agent CLASSic mean | 5.5 | 5.7 | +0.2 |
| Skill mean | 8.7 | 9.1 | +0.4 |
| Agent validator checks | 8 | 10 | +25% |
| Skill validator checks | 13 | 15 | +15% |
| Regressions | -- | 0 | None |

See [delta-report.md](grading/delta-report.md) for full analysis.

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
