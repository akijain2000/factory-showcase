---
name: 08-rfc-template-writer
description: Generates RFC (Request for Comments) documents for proposed technical changes by gathering requirements, evaluating alternatives, and filling a structured template with motivation, design, trade-offs, and migration plan. Use when proposing an architecture change, introducing a new system, or documenting a technical decision that needs team review.
---

# RFC Template Writer

Produce a complete RFC document ready for team review from a description of a proposed change.

## Procedure

1. **Gather context.** Ask for or identify: the problem being solved, who is affected, what the current state is, and what constraints exist (timeline, budget, compatibility).

2. **Evaluate alternatives.** List at least two approaches (including "do nothing"). For each, note pros, cons, effort, and risk.

3. **Select recommendation.** Pick the approach that best fits the constraints. State the reasoning explicitly.

4. **Fill the RFC template.** Use the template below. Every section must have content; write "N/A — [reason]" if a section genuinely does not apply.

5. **Review for completeness.** Verify: motivation is concrete (not "improve things"), alternatives have real trade-offs (not strawmen), migration plan has actionable steps, and rollback is possible.

## RFC output template

```markdown
# RFC: [Title]

**Author:** [name]
**Status:** Draft
**Created:** [date]
**Last updated:** [date]

## 1. Summary

<!-- 2-4 sentences: what is being proposed and why -->

## 2. Motivation

<!-- What problem does this solve? Who is affected? What happens if we do nothing? -->

## 3. Current state

<!-- How does the system work today? Include a diagram if helpful. -->

## 4. Proposed design

<!-- Detailed description of the proposed change. Include:
     - Architecture / data flow
     - API changes
     - New dependencies
     - Configuration changes -->

## 5. Alternatives considered

| Approach | Pros | Cons | Effort | Recommendation |
|----------|------|------|--------|----------------|
| Option A | ... | ... | ... | Recommended |
| Option B | ... | ... | ... | Rejected |
| Do nothing | ... | ... | None | Rejected |

## 6. Migration plan

<!-- Step-by-step plan for rolling out the change:
     1. ...
     2. ...
     Rollback: ... -->

## 7. Security and privacy

<!-- Impact on auth, data handling, secrets, compliance. "No impact" if none, with reasoning. -->

## 8. Testing plan

<!-- How will the change be validated? Unit, integration, staging, canary? -->

## 9. Observability

<!-- New metrics, alerts, dashboards, log changes. -->

## 10. Timeline and milestones

| Milestone | Target date | Owner |
|-----------|-------------|-------|
| ... | ... | ... |

## 11. Open questions

<!-- Unresolved decisions or unknowns that need input before finalizing. -->

## 12. References

<!-- Links to related RFCs, design docs, tickets, prior art. -->
```

## Gotchas

- Strawman alternatives: every rejected option should have at least one genuine advantage. If it has none, it is not a real alternative.
- Vague motivation: "improve performance" is not a motivation. State the measured or observed problem and the target metric.
- Missing rollback: every migration plan needs a rollback section. "We cannot roll back" is an acceptable answer but must be stated explicitly with the reason.
- RFC scope creep: one RFC per decision. If the proposal bundles unrelated changes, split into separate RFCs.
