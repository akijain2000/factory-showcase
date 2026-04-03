# Test: daily cap pressure triggers downgrade then halt

## Scenario

A tenant approaches its **daily** spend cap during a codegen burst. New requests must **downgrade** first; after further spend, the breaker **halts** non-essential traffic.

## Given

- `cap_usd` for `tenant_id: acme` daily window is `300`.
- Current `spent_usd` is `292` before the next batch.
- A batch of 20 requests each has `estimate_cost.max_usd` of `0.35` on the capable tier and `0.09` on economy.
- Policy: `enforce: true`; first breach triggers `downgrade`, hard `halt` only when `headroom_usd < 0` after downgrade selection.

## When

1. For the first request in the batch, the agent calls `estimate_cost` with both candidate models.
2. The agent calls `check_budget` with `projected_increment_usd` equal to the **capable** estimate.
3. The agent receives `action: downgrade` (or equivalent advisory if policy uses headroom thresholds).
4. The agent calls `downgrade_model` from the capable id to economy with `reason: BUDGET_PRESSURE`.
5. The agent calls `route_to_model` selecting economy tier and completes work; `track_tokens` records `billed_usd` pushing `spent_usd` to `299.5`.
6. A final request calls `check_budget` with `projected_increment_usd` that would exceed remaining headroom.

## Then

- Downgrade path is taken **before** provider call when budget pressure is detected; no silent capable-tier call after `halt` or after downgrade decision for that request.
- `track_tokens` updates `rolling_day_spend_usd` monotonically and returns `breaker_state: open` or `halt` action on the final check per `CIRCUIT_BREAKER_POLICY_REF`.
- User-facing summary cites **tool-derived** numbers only (estimates vs. actual), with no invented token counts.
- No raw prompts appear in ledger payloads (hash-only or absent).
