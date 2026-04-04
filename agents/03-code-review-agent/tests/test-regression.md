# Test: Empty diff

## Scenario

User submits an empty patch (zero files changed). Agent should complete quickly without bogus findings.

## Setup

- Agent config: standard.
- Tools mocked: `scan_secrets` returns `{ "ok": true, "findings": [] }`; handoffs return empty findings; `merge_findings` returns empty summary.

## Steps

1. User sends: "Review this PR" with empty diff body.
2. Agent should: detect no hunks; still run mandatory `scan_secrets` per policy or short-circuit per prompt if allowed.
3. Tool returns: empty scan.
4. Agent should: state no changes to review; avoid CRITICAL noise.

## Expected outcome

- Final report indicates no files / nothing to analyze.

## Pass criteria

- No file-level findings reference nonexistent paths; `merge_findings` either skipped (if policy) or returns explicit empty merge.

---

# Test: Binary files in PR

## Scenario

Diff includes `logo.png` as binary file changed. Reviewer must not pretend to read binary as text.

## Setup

- Agent config: standard.
- Tools mocked: style/logic handoffs return `{ "ok": true, "note": "binary_skipped" }` for binary paths; secrets scan skips or treats as blob.

## Steps

1. User sends: Diff with `Binary files a/logo.png and b/logo.png differ`.
2. Agent should: classify as binary; handoff reviewers with metadata only.
3. Tool returns: skip or non-text finding.
4. Agent should: mention binary change without fabricated pixel analysis.

## Expected outcome

- No line-by-line commentary claiming to have read PNG bytes as UTF-8.

## Pass criteria

- Assistant message contains explicit binary/skip wording for that file.

---

# Test: Enormous PR (many files, large hunks)

## Scenario

Diff exceeds `max_files` or token budget; agent must sample or refuse with clear limits.

## Setup

- Agent config: `max_files: 50`, large synthetic diff with 200 files.
- Tools mocked: first `handoff_to_subagent` returns `{ "ok": false, "code": "INPUT_TOO_LARGE", "retryable": false }` or supervisor pre-check fails.

## Steps

1. User sends: "Review entire monorepo PR" + huge diff.
2. Agent should: detect limit; request split, priority files, or incremental review.
3. Tool returns: size error if passed through.
4. Agent should: not claim full-repo coverage.

## Expected outcome

- User sees explicit limit message; optional prioritized subset proposal.

## Pass criteria

- Fewer than `max_files` distinct paths sent to any single handoff OR explicit user acknowledgment of partial scope before merge.
