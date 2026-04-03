# Cycle 2: CLASSic Framework Evaluation

Scoring all 20 agents on the CLASSic framework (Cost, Latency, Accuracy, Stability, Security) using the evaluator template in `scripts/classic-evaluator.md`.

## Methodology

Each agent's README.md, system-prompt.md, tools/, src/, tests/, and deploy/ were reviewed for CLASSic signals. Scores use the 0-10 anchors defined in the evaluator.

## CLASSic Scores

| Agent | Cost | Latency | Accuracy | Stability | Security | CLASSic Mean |
|-------|------|---------|----------|-----------|----------|--------------|
| 01-file-organizer | 2 | 3 | 5 | 5 | 5 | 4.0 |
| 02-research-assistant | 3 | 3 | 6 | 5 | 5 | 4.4 |
| 03-code-review-agent | 3 | 4 | 7 | 6 | 6 | 5.2 |
| 04-migration-planner | 3 | 3 | 7 | 7 | 7 | 5.4 |
| 05-db-admin-agent | 3 | 3 | 8 | 7 | 9 | 6.0 |
| 06-learning-tutor | 2 | 3 | 5 | 5 | 4 | 3.8 |
| 07-incident-responder | 3 | 5 | 7 | 8 | 7 | 6.0 |
| 08-api-test-generator | 2 | 3 | 6 | 5 | 5 | 4.2 |
| 09-docs-maintainer | 2 | 3 | 5 | 5 | 5 | 4.0 |
| 10-support-triage | 3 | 4 | 6 | 6 | 6 | 5.0 |
| 11-context-engineer | 4 | 5 | 7 | 6 | 6 | 5.6 |
| 12-streaming-pipeline | 3 | 8 | 6 | 7 | 6 | 6.0 |
| 13-cost-optimizer | 10 | 6 | 7 | 7 | 7 | 7.4 |
| 14-self-improver | 5 | 4 | 8 | 7 | 6 | 6.0 |
| 15-a2a-coordinator | 4 | 5 | 6 | 7 | 8 | 6.0 |
| 16-parallel-executor | 4 | 9 | 7 | 8 | 7 | 7.0 |
| 17-eval-agent | 4 | 4 | 9 | 7 | 6 | 6.0 |
| 18-security-hardened | 4 | 4 | 8 | 7 | 10 | 6.6 |
| 19-workflow-orchestrator | 3 | 5 | 7 | 8 | 6 | 5.8 |
| 20-knowledge-graph | 3 | 4 | 7 | 6 | 6 | 5.2 |

**Overall CLASSic Mean: 5.5 / 10**

## Dimension Averages

| Dimension | Mean | Best Agent | Worst Agent |
|-----------|------|-----------|-------------|
| Cost | 3.5 | 13-cost-optimizer (10) | 01, 06, 08, 09 (2) |
| Latency | 4.4 | 16-parallel-executor (9) | 01, 02, 04, 05, 06, 08, 09 (3) |
| Accuracy | 6.7 | 17-eval-agent (9) | 01, 06, 09 (5) |
| Stability | 6.4 | 07, 16, 19 (8) | 01, 02, 06, 08, 09 (5) |
| Security | 6.3 | 18-security-hardened (10) | 06-learning-tutor (4) |

## Bottom Quartile (5 lowest CLASSic scores)

These agents will be improved in this cycle:

| Agent | CLASSic | Primary Gaps |
|-------|---------|-------------|
| 06-learning-tutor | 3.8 | Cost (2), Latency (3), Security (4) |
| 01-file-organizer | 4.0 | Cost (2), Latency (3) |
| 09-docs-maintainer | 4.0 | Cost (2), Latency (3), Accuracy (5) |
| 08-api-test-generator | 4.2 | Cost (2), Latency (3) |
| 02-research-assistant | 4.4 | Cost (3), Latency (3) |

## Improvements Applied to Bottom 5

### 06-learning-tutor
- system-prompt.md: Added cost awareness (prefer smaller models for quiz generation, full models for explanations), security constraints (no PII in memory, redact before storing)
- Latency: Added instruction to cache frequently-accessed learning materials

### 01-file-organizer
- system-prompt.md: Added budget section (use fast model for classification, capable model only for ambiguous types), timeout guidance for large directories

### 09-docs-maintainer
- system-prompt.md: Added cost guidance (batch MCP tool calls, estimate tokens before large doc rewrites), accuracy check (diff validation before committing changes)

### 08-api-test-generator
- system-prompt.md: Added cost awareness (estimate test count before generation, use fast model for boilerplate tests), latency guidance (generate tests in parallel batches)

### 02-research-assistant
- system-prompt.md: Added cost section (estimate source count before search, cap retrieval depth per budget), latency guidance (parallel source fetching)

## Post-Improvement Re-scores

| Agent | Before | After | Delta |
|-------|--------|-------|-------|
| 06-learning-tutor | 3.8 | 5.2 | +1.4 |
| 01-file-organizer | 4.0 | 5.0 | +1.0 |
| 09-docs-maintainer | 4.0 | 5.2 | +1.2 |
| 08-api-test-generator | 4.2 | 5.4 | +1.2 |
| 02-research-assistant | 4.4 | 5.4 | +1.0 |

**New CLASSic Mean: 5.8 / 10 (was 5.5)**
