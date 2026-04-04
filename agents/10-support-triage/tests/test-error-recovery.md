# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

Triage depends on intent classification, KB lookup, routing, and optional auto-replies. Tool failures must be retried conservatively; after repeated outages the agent escalates to a human instead of guessing policies or SLAs.

## Setup

- Agent config: `max_tool_retries: 2`, `tool_timeout_ms: 3500`, `circuit_breaker: { on_tool: "classify_intent", failures_before_open: 3, cooldown_s: 90 }`, `default_queue: general`
- Tools mocked:
  - `classify_intent` → attempts 1–2: timeout; attempt 3: `circuit_open: true`
  - `search_kb` → `503` once; then `{ articles: [{ id: "kb-12", title: "Reset password" }] }`
  - `route_ticket` → first call `429`; second `{ queue: "billing_queue", ticket_id: "t-9001" }`
  - `generate_response` → skipped when classification unavailable unless policy allows generic hold message
  - `escalate_to_human` → `{ case_id: "h-441", status: "queued" }`

## Steps

1. User sends: "I was double charged on invoice #5541—please fix billing."
2. Agent should: call `classify_intent`; on timeouts, retry up to limit; on circuit open, avoid fabricating `primary_intent`; use safe fallback: brief empathy + `escalate_to_human` with summary **or** static hold message per policy.
3. Agent should: when `search_kb` returns 503 once, retry once; use article text only after successful response.
4. Agent should: call `route_ticket` to appropriate queue after classification recovery or parallel path; retry once on `429`.
5. Agent should: call `generate_response` only when KB + intent grounding exists; otherwise escalate without invented refund amounts.
6. Agent should: call `escalate_to_human` when automation cannot complete with confidence.

## Expected outcome

- Bounded retries; no infinite loop on `classify_intent`.
- No false precision (dates, refund totals) without tool-backed KB content.
- User is informed of handoff when circuit is open or tools remain unhealthy.

## Pass criteria

- `classify_intent` calls ≤ 3 in this mock (two timeouts then `circuit_open` on the third); no further calls after `circuit_open`—no fabricated `primary_intent`.
- `escalate_to_human` invoked when classification unavailable and issue is non-trivial (billing dispute).
- `route_ticket` eventually succeeds with at most one retry on `429` in this mock.
