# AdaRubric Generator

Task-adaptive evaluation rubric generator for AI agent projects. Instead of fixed grading dimensions, this template generates domain-specific rubrics per agent type.

Based on AdaRubric (arXiv:2603.21362, March 2026): three-stage pipeline of Rubric Generation, Trajectory Evaluation, and Dimension-Aware Filtering.

## How It Works

### Stage 1: Rubric Generation

Given an agent's task description and domain, generate N orthogonal evaluation dimensions with calibrated 5-point scoring criteria.

**Input**: Agent README.md (purpose, architecture, domain)
**Output**: 5 domain-specific dimensions, each with:
- Dimension name
- What it measures (1 sentence)
- 5-point scale (1 = failure, 3 = adequate, 5 = excellent)

### Stage 2: Trajectory Evaluation

Score the agent's design artifacts (system prompt, tools, tests) against each dimension.

**Input**: Generated rubric + agent files
**Output**: Per-dimension score (1-5) with evidence citation

### Stage 3: Dimension-Aware Filtering

Apply the DimensionAwareFilter: a high score on one dimension cannot mask a failure on another. Any dimension below 2/5 is flagged regardless of aggregate.

**Input**: Scored dimensions
**Output**: Overall assessment + flagged weak dimensions

## Rubric Generation Template

For agent type `{AGENT_TYPE}` with domain `{DOMAIN}`:

### Universal Dimensions (always included)
1. **Task Completion Fidelity** - Does the agent accomplish its stated purpose end-to-end?
2. **Failure Mode Coverage** - Are error paths, edge cases, and degraded states handled?

### Domain-Specific Dimensions (3 generated per agent)
Generated based on what matters most for this agent's specific task domain.

Examples:
- Code review agent -> "Coverage Completeness", "False Positive Rate", "Actionability"
- DB admin agent -> "DDL Safety", "Query Optimization Quality", "Backup Discipline"
- Cost optimizer -> "Routing Precision", "Budget Adherence", "Degradation Grace"

## Scoring Anchors

| Score | Meaning |
|-------|---------|
| 1 | Absent or broken - dimension not addressed |
| 2 | Minimal - acknowledged but insufficient |
| 3 | Adequate - meets basic expectations |
| 4 | Strong - exceeds expectations with thoughtful design |
| 5 | Excellent - best-in-class implementation of this dimension |

## Application

1. Read agent README to determine task type and domain
2. Generate 5 dimensions (2 universal + 3 domain-specific)
3. Read system-prompt.md, tools/, tests/ for evidence
4. Score each dimension 1-5
5. Flag any dimension below 2 for immediate improvement
6. Report AdaRubric score as mean of 5 dimensions
