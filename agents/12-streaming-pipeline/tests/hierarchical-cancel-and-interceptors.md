# Test: hierarchical cancel with interceptor ordering

## Scenario

A multi-stage LLM token pipeline shows rising lag on partition 1 only. Operators want to **drain** a subtree tied to one job without killing the global consumer group.

## Given

- Topics: `llm.tokens.v1` and `llm.tool_calls.v1` share an interceptor chain: `metrics` → `pii_redact` → `rate_limit`.
- A new interceptor `enrich` is registered with `order_key` between `pii_redact` and `rate_limit`.
- Scope graph: `job/9001` → children `job/9001/window-a`, `job/9001/window-b`.
- `inspect_backpressure` reports `lag_max_seconds: 55` for group `llm-workers` and elevated pending on partition 1.

## When

1. The agent calls `register_interceptor` for `enrich` on topic pattern `llm.*` with phase `pre_dispatch`.
2. The agent calls `inspect_backpressure` with `topics` including both topic names.
3. The agent calls `cancel_subtree` with `scope_id: job/9001/window-b`, `propagate_to: children`, `grace_ms: 1500`, and `reason_code: HOT_PARTITION_ISOLATION`.
4. The agent avoids `cancel_subtree` on `STREAM_ROOT_SCOPE_ID`.

## Then

- `register_interceptor` returns `ok: true` and `effective_order` lists `enrich` **after** `pii_redact` and **before** `rate_limit`; no `ORDERING_CONFLICT`.
- After cancellation, `inspect_backpressure` shows **reduced** pending on partition 1 relative to pre-cancel snapshot **or** a documented `already_terminal` if the subtree was empty (test accepts either with explicit assertion branch).
- Global consumer group remains **attached**; no `force: true` was required.
- Audit log contains `reason_code` and **not** full payloads from `redacted_samples`.
