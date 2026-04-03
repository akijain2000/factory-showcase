---
name: s11-context-engineering
description: Curates agent context with ACE-style packing and reflection checkpoints. Use when token budgets are tight or long sessions need stable recall for agent 11-context-engineer.
---

# ACE context curation and reflection

## Goal / overview

Keep the working context small, ordered, and honest: pack only what changes outcomes, mark uncertainty, and refresh summaries after meaningful edits. This pairs with **agent 11-context-engineer** for handoffs and long-horizon tasks.

## When to use

- A session exceeds a few thousand tokens of scratch notes, logs, or pasted files.
- The same facts get re-derived on every turn because nothing was promoted to "pinned" context.
- Handoffs between tools or humans need a single snapshot of intent, constraints, and open questions.

## Steps

1. **Inventory**: List current artifacts (goal, constraints, files touched, decisions, failures). Drop duplicates and raw dumps that are recoverable from disk or URLs.
2. **Classify**: Tag each remaining item as *fact*, *hypothesis*, *procedure*, or *noise*. Demote noise; keep facts and procedures near the top.
3. **ACE pack**: Build three layers—**A**ctive (what the next action needs), **C**ondensed history (bullets of what changed and why), **E**xternal pointers (paths, commit SHAs, ticket IDs) instead of inlined blobs.
4. **Reflection pass**: After a substantive tool result or code edit, append a 3–5 line reflection: what worked, what failed, what to try next. Replace stale reflections; do not stack contradictions.
5. **Budget check**: If over budget, shrink layer C first, then move long references to `references/` or file paths cited in layer E.
6. **Handoff block**: Emit a final block: goal one line, blockers one line, next step one line, plus pointers for the receiver.

## Output format

```markdown
## Context pack

Structured bundle for the next turn or handoff; keep each subsection limited to material that changes what the agent does next.

### Active
- ...

### Condensed history
- ...

### External pointers
- ...

## Reflection (latest)
- ...

## Handoff
- Goal:
- Blocker:
- Next:
- Pointers:
```

## Gotchas

- Pasting full file contents repeatedly burns budget without adding new information.
- Mixing user instructions with retrieved text without labeling sources invites goal drift; label each block's origin.
- Reflection that only restates the plan adds no value; require a delta from the prior turn.

## Test scenarios

1. **Activation**: Given a 4k-token chat log and a 1.5k token budget, produce a context pack that preserves the goal, two concrete file paths, and one failed attempt with its lesson—under the budget.
2. **Workflow**: After a simulated bugfix (diff + test output), append a reflection that states what changed in behavior and what remains untested.
3. **Edge case**: When two "facts" conflict (e.g. different API versions in snippets), keep both labeled as conflicting, add a single line recommending verification, and do not merge them into one false certainty.
