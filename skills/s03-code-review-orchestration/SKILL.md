---
name: s03-code-review-orchestration
description: Coordinates multiple reviewers, deduplicates feedback, and sequences merge decisions. Use when several reviewers overlap, comment volume is high, or agent 03-code-review-agent runs a batched review.
---

# Code review orchestration across reviewers

## Goal / overview

Turn overlapping review threads into one ordered set of actions: unique issues, agreed severity, and a clear merge or revise path. Pairs with agent `03-code-review-agent`.

## When to use

- More than one reviewer commented on the same diff region or concern.
- The team needs a single summary before author pushback or merge.
- Review rounds repeat (request changes → fix → re-review) and drift must be tracked.

## Steps

1. **Ingest comments**: collect by file and line range; preserve reviewer id, timestamp, and verbatim text.
2. **Cluster by topic**: group comments that target the same behavior, API, or risk even if wording differs (e.g. "SQL injection" vs "sanitize input").
3. **Deduplicate**: within each cluster, keep one canonical finding; attach alternate phrasings as notes and list all reviewer ids who raised it.
4. **Severity and type**: tag each cluster as bug, security, performance, style, test gap, or question; assign blocking vs non-blocking using team rules or default (security/data loss = blocking).
5. **Resolve conflicts**: when reviewers disagree, document both positions and pick a default action (e.g. escalate to owner, require test, defer to style guide).
6. **Merge strategy**: order fixes by dependency (shared types before callers); define minimum re-review scope (full vs touched files only).

## Output format

- **Finding list**: stable id per cluster, severity, blocking flag, file/line span, canonical description, reviewer ids, status (open/addressed/wontfix).
- **Author checklist**: ordered tasks with pointers back to finding ids.
- **Merge recommendation**: merge / merge with follow-ups / hold, with explicit conditions.

## Gotchas

- "Nit" comments still need clustering if five people repeat the same nit; batch or auto-fix rules reduce noise.
- Outdated comments on superseded commits should be marked stale after rebase, not merged into severity blindly.
- Dismissed threads without rationale should not disappear from the audit trail if compliance matters.

## Test scenarios

1. **Triple duplicate**: Three reviewers flag the same missing null check on one line; output should show one finding with three attestations, not three separate blockers.
2. **Split opinion**: Reviewer A requests a full rewrite; Reviewer B approves with minor nits; orchestration should surface the conflict and propose escalation or tie-break criteria.
3. **Cross-file same issue**: Identical pattern copied in three files gets three comment threads; output should cluster into one pattern-level finding with a multi-file checklist.
