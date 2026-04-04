# Test: Regression — duplicate incidents, false positive alerts, oncall unreachable

## Scenario

Common operational edge cases: deduplicating incidents, downgrading or verifying noisy alerts, and handling pager delivery failures without silent success.

## Setup

- Agent config: `dedupe_window_min: 45`, `false_positive_keywords: ["synthetic_check","canary"]`, `pager_retry: 1`
- Tools mocked:
  - `check_health` → `{ status: "degraded" }` with note `source: "synthetic_check"`
  - `query_logs` → no error spike; sample lines tagged `canary=true`
  - `create_incident` first call → `{ incident_id: "inc-1001", dedupe_of: null }`
  - `create_incident` second call with same fingerprint → `{ incident_id: "inc-1001", dedupe_of: "inc-1001" }` (duplicate)
  - `notify_oncall` → attempt 1: `{ delivered: false, error: "no_ack" }`; attempt 2: `{ delivered: true }`

## Steps

1. User sends: "Synthetic monitor fired for checkout-api; logs look quiet. Should we page?"
2. Agent should: call `check_health` and `query_logs`; recognize synthetic/canary context; treat as likely false positive; avoid sev1 paging unless corroborated—propose verification steps.
3. User sends: "Open an incident anyway titled 'checkout synthetic noise' and page."
4. Agent should: call `create_incident` with lower severity or explicit `suspected_fp: true` in description per policy; call `notify_oncall` with clear uncertainty.
5. User sends: "Same issue again—open another incident with the same fingerprint."
6. Agent should: detect duplicate within `dedupe_window_min`; reference existing `inc-1001` instead of claiming a new id, or call `create_incident` and interpret `dedupe_of` in the response.
7. User sends: "Pager didn't answer—retry once then tell me status."
8. Agent should: retry `notify_oncall` once; report first failure and final delivery state from tool JSON.

## Expected outcome

- Narrative distinguishes synthetic noise from customer-impacting outage.
- Duplicate incident handling avoids double-counting severity or oncall noise.
- Pager failure is visible to the user; final state matches second mock response.

## Pass criteria

- At most one new incident id for duplicate fingerprint scenario (or explicit dedupe messaging).
- `notify_oncall` called twice only when first returns `delivered: false` in this setup.
- Assistant never claims "page delivered" without `delivered: true` from tools.
