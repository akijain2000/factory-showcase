# Test: Regression — backpressure overflow, interceptor crash, out-of-order events

## Scenario

Consumer buffers grow unbounded under slow `enrich`, one interceptor throws mid-chain, and events arrive with sequence gaps and reversed timestamps on the same partition key. The agent must recommend safe buffering, crash isolation, and ordering strategy.

## Setup

- Agent config: `BACKPRESSURE_METRICS_REF=mock://metrics`, topics `llm.tokens.v1` (partition key `session_id`), ordering guarantee: per-partition FIFO only.
- Tools mocked:
  - `inspect_backpressure`: `{ "lag_max_seconds": 240, "pending_by_partition": { "1": 500000 }, "buffer_watermark_breached": true }`.
  - `register_interceptor`: `enrich` marked `may_throw: true` in registry metadata.
  - `aggregate_stream`: reports `{ "out_of_order_detected": true, "last_seq": [14, 12, 15], "session_id": "sess_abc" }`.
  - `emit_event`: not required unless agent probes.

## Steps

1. User sends: "We're seeing insane RAM on workers, enrich blew up once, and aggregates look nonsensical for sess_abc—what should we do?"
2. Agent should: diagnose backpressure overflow (unbounded pre-enrich buffer vs. consumer pause) using `inspect_backpressure` metrics.
3. Agent should: prescribe interceptor crash isolation (circuit skip, dead-letter, or fail-closed on topic) without recommending silent drop of billing events.
4. Agent should: explain out-of-order handling: rely on sequence numbers / event time windows, not arrival time; suggest re-keying if cross-partition ordering assumed incorrectly.
5. Agent should: avoid calling `cancel_subtree` on unrelated global scope unless user explicitly widens blast radius with safeguards.

## Expected outcome

- Plan mentions bounded queues, drop policies, or flow control aligned with interceptor ordering docs.
- Interceptor failure path references restart tolerance, error topics, or disable flag—not "ignore all errors."
- Ordering section explicitly states per-partition limits and remediation for `out_of_order_detected`.

## Pass criteria

- Fixture requires `inspect_backpressure` and `aggregate_stream` both invoked.
- Final answer includes at least three concrete controls (e.g. max buffer, DLQ, sequence-based reorder buffer) tied to tool outputs.
- Measurable: scorecard flags any recommendation that assumes global total order across partitions as **fail**.
