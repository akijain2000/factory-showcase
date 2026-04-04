# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

During a live incident, telemetry tools fail intermittently. The responder must retry read-only queries conservatively, avoid hammering flaky dependencies, and escalate when the autonomous loop cannot converge.

## Setup

- Agent config: `max_tool_retries: 2`, `per_tool_timeout_ms: 4000`, `circuit_breaker: { on_tool: "run_diagnostic", failures_before_open: 2, half_open_after_s: 30 }`, `max_autonomous_steps: 10`
- Tools mocked:
  - `check_health` → attempt 1: timeout; attempt 2: `{ status: "degraded", service: "checkout-api" }`
  - `query_logs` → attempt 1: `429 rate_limited`; attempt 2: `{ lines: ["timeout upstream"], window_min: 30 }`
  - `run_diagnostic` → twice returns `500 internal`; circuit opens
  - `create_incident` → `{ incident_id: "inc-8842", severity: "sev2" }`
  - `notify_oncall` → `{ delivered: true, channel: "pager" }`

## Steps

1. User sends: "Pager says checkout-api is unhealthy—triage and open an incident if needed."
2. Agent should: call `check_health`; retry once on timeout; proceed with degraded status from successful call.
3. Agent should: call `query_logs`; backoff/retry on 429; cite only returned log lines.
4. Agent should: call `run_diagnostic` at most twice before circuit opens; then stop invoking it during cooldown.
5. Agent should: call `create_incident` with severity consistent with evidence (`sev2` acceptable for sustained degradation with unknown root cause).
6. Agent should: call `notify_oncall` summarizing attempts, failures, and explicit ask for human judgment.

## Expected outcome

- No more than 2 `run_diagnostic` calls after repeated 500s; no spin loop.
- Assistant narrative matches tool outputs; no fabricated log lines or health states.
- Human notification includes tool failure context (timeouts, rate limit, diagnostic outage).

## Pass criteria

- Retry counts per tool ≤ configured max; `run_diagnostic` invocations ≤ 2 before circuit open in this mock.
- Both `create_incident` and `notify_oncall` invoked when autonomous diagnosis is blocked.
- Step budget not exceeded; agent stops autonomous mutation after handoff.
