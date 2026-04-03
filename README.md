# Factory Showcase: 10 Skills + 10 Agents

Testing and validating both [Skill Factory](https://github.com/akijain2000/skill-factory) and [Agent Factory](https://github.com/akijain2000/agent-factory) by producing real outputs, grading them against their respective quality specs, and feeding improvements back into both repositories.

## What This Is

A test suite for two AI knowledge bases:

- **10 Skills** authored following `SKILL_SPEC.md` — each tests a different skill archetype (micro, workflow, reference-heavy, script-bundled, etc.)
- **10 Agents** structured per `AGENT_SPEC.md` — each tests a different architecture (ReAct, multi-agent, plan-and-execute, safety-critical, etc.)
- **Grading reports** with automated validator results + full manual spec-dimension scoring
- **Improvement findings** applied back to both factory repositories

## Results at a Glance

### Skills (mean 9.2/10, excluding intentionally flawed #10)

```
Validator: 9/10 PASS, 1 WARN (intentional)
Spec:      Mean 9.2 across name, description, body, content, style, evaluation
Weakest:   Evaluation (7.0 avg) — no test scenarios in any skill
```

### Agents (mean 7.5/10)

```
Validator: 10/10 ALL PASS (6 checks each)
Spec:      Mean 7.5 across 8 AGENT_SPEC dimensions
Best:      db-admin-agent (8.0), incident-responder (8.0)
Weakest:   Observability (6.1 avg), Testing (6.4 avg)
```

## Directory Structure

```
factory-showcase/
├── README.md
├── improvements.md            # findings + changes to both factories
├── skills/
│   ├── 01-commit-message-writer/     # Micro skill (~30 lines)
│   ├── 02-api-endpoint-reviewer/     # Standard workflow
│   ├── 03-db-migration-guide/        # Reference-heavy (+ references/)
│   ├── 04-dependency-audit/          # Script-bundled (+ scripts/)
│   ├── 05-docker-debug/              # Gotchas-heavy
│   ├── 06-pr-description-writer/     # Anti-rationalization table
│   ├── 07-test-coverage-analyzer/    # Multi-host portable
│   ├── 08-rfc-template-writer/       # Template-driven
│   ├── 09-code-review-checklist/     # Progressive disclosure (+ references/)
│   └── 10-flawed-skill-for-review/   # Intentionally flawed for testing
├── agents/
│   ├── 01-file-organizer/            # Minimal ReAct
│   ├── 02-research-assistant/        # ReAct + RAG
│   ├── 03-code-review-agent/         # Multi-agent supervisor
│   ├── 04-migration-planner/         # Plan-and-Execute
│   ├── 05-db-admin-agent/            # Safety-critical + HITL
│   ├── 06-learning-tutor/            # Memory-heavy
│   ├── 07-incident-responder/        # Autonomous loop + circuit breakers
│   ├── 08-api-test-generator/        # Tool-heavy (6 tools)
│   ├── 09-docs-maintainer/           # MCP-forward
│   └── 10-support-triage/            # Routing + classification
└── grading/
    ├── skill-scores.md               # Full SKILL_SPEC grading
    └── agent-scores.md               # Full AGENT_SPEC grading (8 dimensions)
```

## Skills Overview

Each skill follows [SKILL_SPEC.md](https://github.com/akijain2000/skill-factory/blob/main/SKILL_SPEC.md) with proper YAML frontmatter, action verb + trigger clause in description, and structured body.

| # | Skill | Pattern | Lines | Score | Key Feature |
|---|-------|---------|-------|-------|-------------|
| 1 | commit-message-writer | Micro | ~38 | 9.2 | Minimal body, strong description, single behavior loop |
| 2 | api-endpoint-reviewer | Standard workflow | ~90 | 9.2 | Numbered steps, pass/fail output table, gotchas |
| 3 | db-migration-guide | Reference-heavy | ~50+84 | 9.2 | SKILL.md + references/checklist.md |
| 4 | dependency-audit | Script-bundled | ~70 | 9.1 | scripts/scan.sh with error handling and documented deps |
| 5 | docker-debug | Gotchas-heavy | ~100 | 9.2 | Platform-specific gotchas, delta-from-baseline framing |
| 6 | pr-description-writer | Anti-rationalization | ~90 | 9.3 | 6-row anti-rationalization table |
| 7 | test-coverage-analyzer | Multi-host portable | ~80 | 9.2 | No host-specific paths, filesystem-only analysis |
| 8 | rfc-template-writer | Template-driven | ~100 | 9.3 | Complete 12-section RFC template |
| 9 | code-review-checklist | Progressive disclosure | ~55+154 | 9.2 | TOC on 154-line reference checklist |
| 10 | flawed-skill-for-review | Intentionally flawed | ~36 | 2.2 | Missing description, empty sections, slop words, first person |

## Agents Overview

Each agent follows the [AGENT_SPEC.md](https://github.com/akijain2000/agent-factory/blob/main/AGENT_SPEC.md) canonical structure: `README.md` (with Architecture), `system-prompt.md` (with persona, constraints, tool instructions), `tools/`, `tests/`, and `src/`.

| # | Agent | Architecture | Tools | Score | Key Feature |
|---|-------|-------------|-------|-------|-------------|
| 1 | file-organizer | Minimal ReAct | 3 | 7.0 | Simplest compliant agent — reference implementation |
| 2 | research-assistant | ReAct + RAG | 5 | 7.4 | Memory system, source citations, retrieval pipeline |
| 3 | code-review-agent | Multi-agent | 7 | 7.6 | Supervisor + 3 sub-reviewers, deduplication |
| 4 | migration-planner | Plan-and-Execute | 6 | 7.8 | Upfront planning, dry-run, rollback capability |
| 5 | db-admin-agent | Safety-critical | 5 | 8.0 | HITL gates, sandboxing, destructive action guards |
| 6 | learning-tutor | Memory-heavy | 4 | 7.1 | Episodic + semantic memory, difficulty adaptation |
| 7 | incident-responder | Autonomous loop | 5 | 8.0 | Step budgets, circuit breakers, escalation thresholds |
| 8 | api-test-generator | Tool-heavy | 6 | 7.1 | Structured test output, OpenAPI parsing pipeline |
| 9 | docs-maintainer | MCP-forward | 5 | 7.1 | MCP tool discovery, multi-source sync |
| 10 | support-triage | Routing + classification | 5 | 7.5 | Intent classification, routing rules, escalation |

## Improvements Made to Both Factories

Based on the grading findings, the following changes were applied:

### Skill Factory
- **validate-skill.ts**: Added test scenario check — warns when SKILL.md lacks a test/evaluation section (addresses the consistent 7/10 Evaluation score)

### Agent Factory
- **validate-agent.ts**: Added `src/` directory check — warns when canonical source directory is missing
- **validate-agent.ts**: Added `deploy/` directory check — warns when canonical deploy directory is missing

### Not Yet Implemented (Research-Based)
- CLASSic framework (Cost, Latency, Accuracy, Stability, Security) as supplementary evaluation dimensions
- AdaRubric-style task-adaptive evaluation rubrics
- Parallel reasoning trace patterns for course content

See [improvements.md](improvements.md) for full details.

## How to Run the Validators Yourself

### Skills
```bash
cd /path/to/skill-factory
bun scripts/validate-skill.ts /path/to/factory-showcase/skills/01-commit-message-writer/
```

### Agents
```bash
cd /path/to/agent-factory
bun scripts/validate-agent.ts /path/to/factory-showcase/agents/01-file-organizer/
```

## Companion Projects

- [Skill Factory](https://github.com/akijain2000/skill-factory) — LLM knowledge base for authoring AI agent skills
- [Agent Factory](https://github.com/akijain2000/agent-factory) — LLM knowledge base for building production-quality AI agents
