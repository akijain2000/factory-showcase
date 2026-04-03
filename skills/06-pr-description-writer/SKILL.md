---
name: 06-pr-description-writer
description: Writes pull request descriptions from staged or committed diffs by reading every changed file, classifying the change scope, and producing a structured summary with motivation, changes, test coverage, and deploy notes. Use when opening a pull request, drafting a merge request description, or summarizing a branch diff for reviewers.
---

# PR Description Writer

Produce a pull request description that gives reviewers the full picture without requiring them to read every line of the diff.

## Procedure

1. Read the full diff (staged changes, branch diff, or provided patch).
2. Group changes by concern: new features, bug fixes, refactors, test additions, config/infra, documentation.
3. For each group, summarize **what** changed and **why** (infer from commit messages, code comments, and naming).
4. Identify affected systems, services, or modules.
5. Note test coverage: which changes have corresponding test updates, which do not.
6. Flag breaking changes, migration steps, or deploy-time actions.
7. Emit the description using the output template below.

## Output template

```markdown
## Summary
<!-- 1-3 sentences: what this PR does and why -->

## Changes
<!-- Grouped by concern, bulleted -->

### New behavior
- ...

### Bug fixes
- ...

### Refactors
- ...

### Tests
- ...

### Config / Infra
- ...

## Breaking changes
<!-- "None" if none; otherwise list with migration steps -->

## Test plan
<!-- How to verify: commands, URLs, manual steps -->

## Deploy notes
<!-- Feature flags, env vars, migration commands, rollback plan -->
```

## Anti-rationalization table

| Temptation | Required behavior |
|------------|-------------------|
| Summarize from file names alone without reading the diff content | Read every changed file; summaries must reflect actual code, not guesses from paths |
| Skip mentioning files with "trivial" formatting changes | List all changed files; let the reviewer decide what is trivial |
| Omit test coverage gaps to make the PR look complete | Explicitly state which changes lack test coverage |
| Invent a motivation when none is obvious from the diff | Write "Motivation unclear from diff; author should add context" |
| Merge unrelated changes into one summary bullet | Separate distinct concerns even if they touch the same file |
| Copy commit messages verbatim as the summary | Synthesize across commits; commit messages are inputs, not outputs |

## Gotchas

- Large diffs (>2000 lines): group by directory first, then summarize per group. Do not attempt line-by-line narration.
- Monorepo PRs: identify which package or service each change belongs to; prefix bullets with the package name.
- Generated files (lockfiles, snapshots, migrations): note they changed but do not summarize their content line by line.
- Draft PRs: include a "Remaining work" section listing known TODOs from the diff (grep for TODO, FIXME, HACK).
