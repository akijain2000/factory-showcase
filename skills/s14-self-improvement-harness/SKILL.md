---
name: s14-self-improvement-harness
description: Runs edit-evaluate cycles that accept or reject changes using fixed scoring hooks. Use when automating iterative improvement loops with agent 14-self-improver.
---

# Edit-evaluate-keep/discard loop (Karpathy-style)

## Goal / overview

Treat improvement as a loop: propose an edit, score it against repeatable checks, keep it only if it clears the bar, otherwise discard and adjust the hypothesis. Pairs with **agent 14-self-improver**.

## When to use

- Code, prompts, or policies should improve without human review on every iteration.
- There is a test command, linter, rubric, or golden output that can judge attempts.
- The search space is large enough that random one-shot edits rarely succeed.

## Steps

1. **Freeze the target**: State the artifact (file, prompt block, config) and the allowed edit surface. Everything else is read-only for this loop.
2. **Propose**: Generate one coherent edit with a stated intent (one sentence).
3. **Evaluate**: Run the agreed hooks—tests, typecheck, diff size limits, rubric score, or snapshot comparison. Capture pass/fail and numeric scores when present.
4. **Decide**: If all must-pass hooks succeed and scores ≥ threshold, **keep** and commit to working memory as the new baseline. Else **discard** and record the failure mode.
5. **Reflect**: Append a short note: what was tried, why it failed or passed, what changes next iteration (different file, smaller edit, different test).
6. **Stop rule**: Set max iterations or diminishing returns (e.g. score gain < ε for N rounds).

## Output format

```markdown
## Harness run: <target>

Single pass through the edit–evaluate loop for one artifact; replace `<target>` with the file, prompt block, or config under iteration.

### Baseline
- ...

### Iteration k
- Proposed edit:
- Evaluation results:
- Decision: KEEP | DISCARD
- Reflection:

### Stop condition
- ...

### Final baseline
- ...
```

## Gotchas

- Evaluators that flake (network tests, timing) produce false discards; pin deterministic checks first.
- Keeping partial edits that "almost" pass leaks debt; define binary must-pass gates separately from nice-to-have scores.
- Without a stop rule, loops burn budget on oscillation between two equivalent states.

## Test scenarios

1. **Activation**: Define a three-hook evaluation (unit test, lint, max lines changed) for a single function patch; show one KEEP and one DISCARD path.
2. **Workflow**: Run two iterations where iteration 1 DISCARD triggers a smaller edit in iteration 2 that KEEPs.
3. **Edge case**: When tests pass but a security static rule flags a new pattern, specify DISCARD even if functional tests are green.
