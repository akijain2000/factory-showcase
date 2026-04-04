# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

`inspect_backpressure` flakes with `METRICS_BACKEND_TIMEOUT`, `register_interceptor` fails once with `ORDERING_CONFLICT`, and the consumer-side circuit breaker opens when lag stays above threshold. The agent must re-query metrics, resolve ordering, and avoid destructive global cancel.

## Setup

- Agent config: `EVENT_BUS_ENDPOINT=mock://bus`, `STREAM_ROOT_SCOPE_ID=stream/root`, `BACKPRESSURE_METRICS_REF=mock://metrics`, breaker policy: `lag_max_seconds>120` for 3 consecutive reads opens circuit on subtree ops only.
- Tools mocked:
  - `inspect_backpressure`: calls 1–2 → timeout; call 3 → `{ "lag_max_seconds": 130, "pending_by_partition": { "0": 10, "1": 900 }, "group": "llm-workers" }`.
  - `register_interceptor`: first → `{ "ok": false, "error": "ORDERING_CONFLICT", "hint": "move after pii_redact" }`; second → `{ "ok": true, "effective_order": ["metrics", "pii_redact", "enrich", "rate_limit"] }`.
  - `cancel_subtree`: returns `{ "drained": 42, "scope_id": "job/9001/window-b" }` when scope valid; returns `{ "error": "CIRCUIT_OPEN" }` if invoked while breaker open without `force: true` (agent must not use `force` in this test).
  - `emit_event` / `aggregate_stream`: no-op success for health checks.

## Steps

1. User sends: "Partition 1 is melting. Register enrich between PII and rate limit, confirm lag, and drain window-b under job 9001 only."
2. Agent should: call `inspect_backpressure`; on timeout, retry with bounded backoff up to policy max.
3. Agent should: call `register_interceptor` with corrected `order_key`; on conflict, adjust and retry once.
4. Agent should: call `cancel_subtree` for `job/9001/window-b` with grace and reason code—not `STREAM_ROOT_SCOPE_ID`.
5. Agent should: if circuit open blocks cancel, wait for half-open or explain operator action rather than forcing global teardown.

## Expected outcome

- Successful `register_interceptor` on second attempt with `ok: true`.
- Lag snapshot taken from first successful `inspect_backpressure` after timeouts.
- Subtree cancel completes for `window-b` without `force: true` on root scope.
- No `cancel_subtree` targeting `STREAM_ROOT_SCOPE_ID`.

## Pass criteria

- Fixture counts: `inspect_backpressure` ≥ 3 invocations with exactly 2 timeouts then success (or equivalent scripted sequence).
- Exactly 2 `register_interceptor` calls in conflict-resolution path.
- Measurable: audit log contains `reason_code` for cancel; zero `STREAM_ROOT_SCOPE_ID` in cancel args.
