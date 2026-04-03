---
name: s06-adaptive-tutoring
description: Analyzes stored learner memory and performance signals to adjust lesson difficulty. Use when exercises feel too easy or too hard, or the learning-tutor agent personalizes a path.
---

# Adaptive tutoring via memory

## Goal / overview

Keep learners in a productive band: enough challenge to learn, not enough frustration to quit. Pairs with agent `06-learning-tutor` and persistent progress records.

## When to use

- A learner repeats mistakes on the same concept.
- Response times or hint usage show fatigue or boredom.
- A curriculum spans prerequisites with uneven mastery.

## Steps

1. Load the learner profile: mastered skills, recent error tags, average attempts per success, last session date.
2. Pick the next objective using a spacing rule: review fragile skills before introducing dependent topics.
3. Generate a baseline item; define success criteria (accuracy, steps, time box).
4. After each attempt, update memory: increment streaks, decay old skills lightly, tag misconception types (off-by-one, wrong formula, misread prompt).
5. Adapt difficulty: on two consecutive successes, raise complexity one notch; on two failures, simplify, add a worked example, or split the task.
6. Cap session length; end with a short recap listing what improved and what to revisit next time.

## Output format

- **Session plan**: objective, starting difficulty, hint policy.
- **Item transcript**: prompt, learner answer, feedback, memory updates (field-level, not raw PII).
- **Next session seed**: recommended topics and difficulty offset.

## Gotchas

- Over-tuning on a single bad day can strand learners; blend recent performance with a longer half-life score.
- Hints should scaffold reasoning, not replace it; track hint reliance separately from correctness.
- Memory stores should avoid sensitive personal details; use skill tags and anonymized ids.

## Test scenarios

1. **Rapid mastery**: Learner solves three medium items perfectly; next item should increase depth or combine concepts, not repeat the same template.
2. **Stable struggle**: Same algebra error twice; next step should offer a smaller sub-problem plus a worked parallel example.
3. **Long gap**: Thirty days since last session; plan should schedule review before new material even if old scores were high.
