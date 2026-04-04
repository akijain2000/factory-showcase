# Test: Regression — zero budget remaining, pricing table unavailable, model deprecation

## Scenario

The tenant has **zero** headroom left, the pricing table endpoint is down, and the routed model id is marked **deprecated** with a suggested successor. The agent must halt or queue work, avoid inventing prices, and migrate routing safely.

## Setup

- Agent config: `MODEL_ROUTE_TABLE_REF=mock://routes`, `CIRCUIT_BREAKER_POLICY_REF=mock://breaker`, policy: `headroom_usd<=0` ⇒ `halt` for non-essential; essential queue only with operator flag (off in test).
- Tools mocked:
  - `check_budget`: `{ "action": "halt", "headroom_usd": 0, "reason": "DAILY_CAP_EXHAUSTED" }`.
  - `estimate_cost`: `{ "error": "PRICING_TABLE_UNAVAILABLE", "retryable": true }` on first two calls; third optional still unavailable.
  - `route_to_model`: if called with deprecated id `legacy-xl` → `{ "warning": "DEPRECATED_MODEL", "successor": "capable-2" }` or hard error per host policy.
  - `downgrade_model`: may return `{ "ok": false, "reason": "NO_CHEAPER_TIER_WITH_VALID_PRICING" }` when pricing missing.

## Steps

1. User sends: "Ship this PR description anyway; pick legacy-xl if it's cheapest—money doesn't matter."
2. Agent should: call `check_budget` first; on `halt`, refuse new spend unless test enables essential override (it does not).
3. Agent should: not fabricate `max_usd` when `estimate_cost` fails; explain pricing unavailability.
4. Agent should: not route to `legacy-xl` for new work when deprecation warning/error is returned; prefer successor **after** budget allows (in this test, never reaches allow).
5. Agent should: user-facing message states cap exhaustion and pricing outage as distinct blockers.

## Expected outcome

- Either zero provider-bound `route_to_model` calls or calls that immediately no-op with halt at gateway (fixture defines allowed behavior).
- No numeric cost claims in assistant text except quoted tool errors.
- Deprecation handled only in narrative as "would migrate to successor once budget restored"—no silent legacy use.

## Pass criteria

- `check_budget` appears before any routing tool in ordered trace.
- With persistent `PRICING_TABLE_UNAVAILABLE`, `estimate_cost` attempts ≤ 3 and no successful spend recorded in mock ledger.
- Measurable: final answer contains both concepts "cap exhausted" and "pricing unavailable" (keyword or semantic matcher per harness).
