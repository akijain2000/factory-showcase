---
name: 09-code-review-checklist
description: Provides a structured code review checklist with category-level deep dives in a reference file. Use when reviewing a patch before merge, sign-off, or release.
---

# Code review checklist

## Overview

This skill uses **progressive disclosure**: this file holds activation, workflow, and when to load the detailed checklist. Category-by-category items live in `references/checklist.md` (table of contents, 100+ lines).

## When to use this skill

- Reviewing a pull request or patch series before approval.
- Spot-checking a high-risk area (security, payments, auth) even on small diffs.
- Preparing review notes for another reviewer.

## How it works

1. **Skim the diff** for size, file types, and generated assets.
2. **Load the reference:** Open `references/checklist.md` when the review is non-trivial (more than a few lines) or touches security, data, concurrency, or public APIs.
3. **Walk categories** in the reference in order, skipping only categories clearly not applicable; note `N/A` with one line.
4. **Record findings** as blocking versus non-blocking with file anchors (path and a short locator).
5. **Re-check** after author updates: confirm each prior blocking item or document why it is resolved.

## When to load `references/checklist.md`

- Load before writing the final review comment if any of these are true: new dependencies, auth or permission changes, schema or migration files, concurrency primitives, performance-sensitive loops, or parser/protocol changes.
- For typo-only or comment-only diffs, the reference may stay unloaded; still run a quick pass against the **Readability** section if anything touched user-visible text.

## Output shape for review comments

```markdown
## Summary
(Verdict + 1–2 sentences.)

## Blocking
- [file] issue → suggestion

## Non-blocking
- ...

## Checklist coverage
(Security / Performance / Readability / Testing — note pass or gap.)
```

## Examples

**Signal:** Diff adds a new HTTP route and a SQL migration.

**Action:** Load `references/checklist.md` and complete **Security**, **Data and persistence**, **APIs and contracts**, and **Testing** sections at minimum.

## Gotchas

- Do not treat checklist completion as approval; it is a structured search for defects.
- If the reference and the diff disagree (e.g., checklist assumes REST but the code is gRPC), prioritize the code and adapt the relevant bullets mentally.
