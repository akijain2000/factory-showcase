---
name: 01-commit-message-writer
description: Drafts conventional commit messages from staged repository diffs. Use when preparing a commit or aligning message format before a push.
---

# Commit message writer

## Goal

Produce a single conventional commit line (optional body) from what is already staged, without inventing scope beyond the diff.

## Inputs

- Staged changes only (`git diff --cached` or equivalent). If nothing is staged, stop and report that staging is required.

## Steps

1. Read the full staged diff: file list plus hunks.
2. Classify the dominant change type using Conventional Commits: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, or `chore` (pick the single best fit for the staged diff).
3. Pick a scope when one primary area stands out (e.g. `auth`, `api`, `ui`); omit scope if the change is broad or unclear.
4. Write the subject: imperative mood, lowercase start after type, no trailing period, roughly 50 characters or fewer when practical.
5. Add a body only if the diff bundles multiple concerns or the subject cannot carry enough context; use bullet lines explaining *why* when non-obvious.

## Output format

```
<type>(<scope>): <subject>

[optional body]
```

## Rules

- Do not reference unstaged or unrelated files.
- Do not include issue numbers unless they already appear in staged edits or the invoker supplied them.
- One commit message per invocation; if the diff mixes unrelated concerns, recommend splitting the commit instead of one vague subject.
- Example shape: `fix(payments): reject zero-amount captures`.
