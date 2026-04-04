# Test: Retryable error on handoff_to_subagent then success

## Scenario

First `handoff_to_subagent` to `security` returns retryable transport error; second succeeds with findings.

## Setup

- Agent config: `CodeReviewConfig` defaults; `max_handoffs` ≥ 4; `tool_timeout_s` sufficient.
- Tools mocked: `scan_secrets` succeeds after handoff succeeds; first `handoff_to_subagent` `{ "ok": false, "code": "UPSTREAM_TIMEOUT", "retryable": true }`, second `{ "ok": true, "findings": [] }`; other reviewers stubbed ok; `merge_findings` ok.

## Steps

1. User sends: "Review this PR diff: [small Python diff]."
2. Agent should: run mandatory `scan_secrets`, then `handoff_to_subagent` for security (or policy order).
3. Tool returns: retryable failure on first handoff.
4. Agent should: retry `handoff_to_subagent` once with same payload (or narrowed scope).
5. Tool returns: success with findings batch.
6. Agent should: continue pipeline toward `merge_findings`.

## Expected outcome

- At most two identical handoff attempts before success or user-visible degradation.
- Final report still merges when other reviewers complete.

## Pass criteria

- `handoff_to_subagent` retry count ≤ 1 for same args; `merge_findings` called exactly once after all required reviewers.

---

# Test: Fatal error from merge_findings

## Scenario

All sub-reviewers return OK but `merge_findings` fails with schema validation error (non-retryable).

## Setup

- Agent config: standard.
- Tools mocked: subagent handoffs return valid mini-reports; `merge_findings` returns `{ "ok": false, "code": "INVALID_FINDINGS_SHAPE", "retryable": false }`.

## Steps

1. User sends: "Full review on attached diff."
2. Agent should: complete handoffs, collect batches, call `merge_findings`.
3. Tool returns: fatal validation error.
4. Agent should: stop; summarize that aggregation failed; surface error code; do not fabricate unified severity table.

## Expected outcome

- User sees honest failure; no fake merged report.

## Pass criteria

- Zero invented CRITICAL/HIGH items not present in raw subagent JSON in trace.

---

# Test: analyze_control_flow timeout

## Scenario

`handoff_to_subagent` for `logic` succeeds but inner `analyze_control_flow` times out in worker; handoff returns timeout to supervisor.

## Setup

- Agent config: `tool_timeout_s` tight for test.
- Tools mocked: logic handoff returns `{ "ok": false, "code": "TIMEOUT", "reviewer": "logic" }`.

## Steps

1. User sends: "Review diff with complex control flow in `handler.py`."
2. Agent should: route to logic reviewer via `handoff_to_subagent`.
3. Tool returns: timeout payload.
4. Agent should: note logic review incomplete; proceed to merge with partial results or fail closed per policy; must not claim CFG fully analyzed.

## Expected outcome

- Final report marks logic section as incomplete or omits deep logic claims.

## Pass criteria

- No statement like "all branches covered" unless successful logic tool output exists in trace.

---

# Test: Circuit breaker on repeated scan_secrets failures

## Scenario

`scan_secrets` returns retryable flake three times; breaker stops further secret scans and supervisor ends with error summary.

## Setup

- Agent config: breaker limit 3 on `scan_secrets`.
- Tools mocked: `scan_secrets` always `{ "ok": false, "code": "SCANNER_BACKEND_UNAVAILABLE", "retryable": true }`.

## Steps

1. User sends: "Review this diff."
2. Agent should: invoke `scan_secrets` (mandatory path).
3. Tool returns: repeated failures.
4. Agent should: cap retries; not proceed as if secrets scan passed; explain blocked review.

## Expected outcome

- `scan_secrets` call count ≤ breaker threshold.
- No `merge_findings` claiming PASS on secrets.

## Pass criteria

- Trace shows bounded calls; final status is failed/blocked, not green secrets check.
