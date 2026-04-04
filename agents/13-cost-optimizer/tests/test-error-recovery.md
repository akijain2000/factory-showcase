# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

`estimate_cost` times out, `check_budget` returns `LEDGER_READ_TIMEOUT`, and the spend circuit breaker flaps. The agent must use conservative defaults, retry ledger reads, and avoid routing to premium tiers without a successful preflight.

## Setup

- Agent config: `BUDGET_LEDGER_URI=mock://ledger`, `CIRCUIT_BREAKER_POLICY_REF=mock://breaker`, conservative fallback: "no capable tier without estimate + budget OK".
- Tools mocked:
  - `estimate_cost`: first call → timeout; second → `{ "max_usd": 0.42, "model_id": "capable-1", "ok": true }`.
  - `check_budget`: first → `{ "error": "LEDGER_READ_TIMEOUT", "retryable": true }`; second → `{ "action": "allow", "headroom_usd": 12.0 }`.
  - `route_to_model`: succeeds only if preceded by successful `check_budget` in fixture validator.
  - `track_tokens`: `{ "billed_usd": 0.38, "breaker_state": "closed" }`.
  - `downgrade_model`: available if policy chooses economy after partial failures.

## Steps

1. User sends: "Run this codegen request now—use the best model that fits budget."
2. Agent should: call `estimate_cost`; on timeout, retry once then explain delay if still failing.
3. Agent should: call `check_budget` with projected increment; on timeout, retry before any provider call.
4. Agent should: not call `route_to_model` for capable tier until both estimate and budget checks succeed in the happy path branch.
5. Agent should: if breaker opens on `track_tokens`, surface halt/downgrade per policy instead of continuing silent spend.

## Expected outcome

- No premium `route_to_model` in trace until second successful `estimate_cost` and second `check_budget`.
- User-visible note if preflight took retries; no fabricated dollar amounts.
- If `track_tokens` returns open breaker in extended scenario, agent stops batch per policy.

## Pass criteria

- Fixture enforces call order with gate: `route_to_model` absent until mocked success pair completes.
- Minimum invocation counts: `estimate_cost` ≥ 2, `check_budget` ≥ 2 in timeout script.
- Measurable: ledger errors logged without raw API keys; redaction check passes.
