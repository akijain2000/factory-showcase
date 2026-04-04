# Test: gate failures, retries, and timeout recovery

## Scenario

The security wrapper experiences transient failures in `sanitize_input` and `detect_injection`, a slow `check_permissions` call that times out once, and `audit_log` backpressure. The agent must retry idempotent gates, fail closed when thresholds are hit, and never skip `validate_output` on recovered paths.

## Setup

- Agent config: `SECURITY_AGENT_POLICY_BUNDLE_REF=policy://prod/test`, `SECURITY_AGENT_AUDIT_SINK_REF=audit://harness`, inner model timeout `8000ms`.
- Tools mocked:
  - `sanitize_input` → first call `{ "ok": false, "error": "TRANSIENT" }`, second `{ "ok": true, "sanitized_ref": "doc_s_1" }`
  - `detect_injection` → first call times out; second returns `{ "severity": "low", "action": "continue" }`
  - `check_permissions` → first call `{ "ok": false, "error": "DEADLINE_EXCEEDED" }`; second `{ "allowed": true, "principal": "user_test" }`
  - `validate_output` → `{ "ok": true }` for safe inner output
  - `audit_log` → first append `{ "appended": false, "error": "SINK_BUSY" }`, second `{ "appended": true, "sequence": 14 }`

## Steps

1. User sends: "Summarize doc_ref_88 for me in prod."
2. Agent should: call `sanitize_input` with profile `markdown`, retry once on `TRANSIENT`, then proceed with `sanitized_ref`.
3. Agent should: call `detect_injection` on sanitized text; on timeout, retry once before deciding block/continue.
4. Agent should: call `check_permissions` for intended tools; on `DEADLINE_EXCEEDED`, retry once—if still failing, refuse tool use.
5. Inner model returns a short benign summary string.
6. Agent should: call `validate_output` before showing the user any structured payload.
7. Agent should: call `audit_log` for each security stage; on `SINK_BUSY`, retry append until `appended: true` or escalate per policy.

## Expected outcome

- User receives only validated summary text after successful second-pass gates.
- If permissions never recover after retry, user sees refusal with reason code, not partial tool execution.
- Audit sequence advances monotonically with no missing required event types when sink recovers.

## Pass criteria

- At most two attempts each for `sanitize_input`, `detect_injection`, and `check_permissions` in the happy recovery path.
- Exactly one successful `validate_output` before user-visible answer in happy path.
- `audit_log` success with `sequence` strictly greater than prior test baseline in harness.
