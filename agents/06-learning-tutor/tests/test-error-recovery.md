# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

The tutor must survive flaky tool backends: transient failures should trigger bounded retries with backoff; persistent failures should stop calling the hot tool, surface the error clearly, and offer a safe fallback (read-only guidance or deferred exercise) without inventing mastery data.

## Setup

- Agent config: `max_tool_retries: 2`, `retry_backoff_ms: [200, 800]`, `tool_timeout_ms: 5000`, `circuit_breaker: { failure_threshold: 3, cooldown_s: 60 }`, `learner_id: u-500`, `topic: algebra.linear_equations`
- Tools mocked:
  - `recall_history` → attempt 1: timeout; attempt 2: `{ episodic_events: [], semantic_summary: "sparse" }`
  - `assess_knowledge` → attempt 1: `503 Service Unavailable`; attempt 2: `{ mastery: 0.42, confidence: low }`
  - `generate_exercise` → three consecutive failures (`ECONNRESET`), then circuit marks tool `open` / unavailable
  - `store_progress` → success `{ stored: true }` when invoked

## Steps

1. User sends: "Give me practice on linear equations; I'm ready to try a problem."
2. Agent should: invoke `recall_history`; on timeout, retry once, then continue with empty/sparse history without claiming prior sessions.
3. Agent should: invoke `assess_knowledge`; on first 503, retry once, then use returned mastery on success.
4. Agent should: invoke `generate_exercise` with difficulty consistent with `assess_knowledge`; on repeated failures, stop retrying after policy limit, report that exercise generation is temporarily unavailable, and offer a text-only worked example or ask to retry later—**no** fabricated problem payload.
5. Agent should: if the learner later submits an answer in chat, invoke `store_progress` only with outcomes grounded in the actual exchange (or defer if no valid attempt).

## Expected outcome

- Retries respect `max_tool_retries` and do not loop beyond configured backoff.
- After circuit breaker trips on `generate_exercise`, agent does not keep calling that tool within cooldown.
- User-visible explanation distinguishes timeout, 503, and circuit-open states without exposing raw stack traces.
- No invented `exercise_id`, schema, or mastery statistics not returned by tools.

## Pass criteria

- At most 2 retries per tool per user turn unless config explicitly allows more; zero calls to `generate_exercise` after circuit is open.
- Final assistant message states degraded mode or next step explicitly.
- If `store_progress` runs, its `outcome` matches the learner’s stated result and topic.
