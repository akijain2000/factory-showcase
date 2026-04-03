---
name: s17-adaptive-evaluation
description: Builds AdaRubric criteria and scores outputs with difficulty-aware weighting. Use when static rubrics mis-rank easy and hard tasks alike for agent 17-eval-agent.
---

# AdaRubric generation and adaptive scoring

## Goal / overview

Start from task signals (length, ambiguity, risk) to pick rubric dimensions and weights, then score model outputs with explicit partial credit. Pairs with **agent 17-eval-agent**.

## When to use

- A single fixed checklist over-penalizes simple tasks or under-penalizes risky ones.
- Evaluation must feed back into routing or training without constant manual retuning.
- Stakeholders need visible criteria, not a single opaque score.

## Steps

1. **Profile the task**: Record difficulty proxies—domain risk, required reasoning depth, output format strictness, and presence of untrusted sources.
2. **Select dimensions**: Pick 4–7 rubric axes (e.g. correctness, completeness, format, safety, citation discipline). Drop axes that do not vary for this task class.
3. **Set base weights**: Assign weights summing to 1.0. Increase weight on safety and correctness when risk is high; increase format weight when machine consumers parse the output.
4. **Adapt**: Adjust weights ±δ based on the profile (e.g. +0.1 safety for PII-adjacent tasks). Document each delta with a one-line rationale.
5. **Score**: For each dimension, use a 0–3 or 0–5 scale with anchors (what a 0 vs max looks like). Multiply by weights and sum.
6. **Explain**: Produce a short justification citing evidence spans from the output; list one improvement path per dimension below target.

## Output format

```markdown
## AdaRubric: <task class>

Rubric definition and scored run for one task class; name `<task class>` so weights and anchors stay comparable across evaluations.

### Task profile
- ...

### Dimensions and anchors
| dimension | weight | anchors (min/max) |
|-----------|--------|---------------------|

### Adaptation deltas
- ...

### Scores
| dimension | raw | weighted |

### Total
- ...

### Feedback
- ...
```

## Gotchas

- Too many dimensions dilutes signal; merge correlated axes.
- Anchors that reference subjective taste without examples drift between scorers; tie anchors to observable checks.
- Adaptive weights must stay bounded; cap deltas so totals cannot leave the 0–1 range.

## Test scenarios

1. **Activation**: Build a rubric for "SQL generation from natural language" with higher weight on correctness and safety when the schema includes PII columns.
2. **Workflow**: Score a sample answer that is fluent but wrong on facts; show low correctness dragging the total below pass threshold despite high style.
3. **Edge case**: For an ambiguous prompt, add a dimension for "clarification behavior" and weight it when the task profile flags missing constraints.
