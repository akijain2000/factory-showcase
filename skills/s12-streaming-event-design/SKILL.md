---
name: s12-streaming-event-design
description: Shapes event envelopes, orders stream interceptors, and plans backpressure behavior. Use when building pipelines, buses, or agent 12-streaming-pipeline processes live event flows.
---

# Streaming event design: envelopes, order, and backpressure

## Goal / overview

Make events self-describing, safe to evolve, and kind to consumers under load. Covers envelope fields, interceptor chains, and explicit backpressure or drop policies. Pairs with agent `12-streaming-pipeline`.

## When to use

- New topics or partitions carry business events across services.
- Middleware (auth, metrics, deduplication) wraps producers or consumers.
- Bursts or slow consumers risk memory growth or unbounded queues.

## Steps

1. **Define the envelope**: stable fields—event name/version, id (unique per emission), occurred time, producer, correlation id, schema version, payload hash or small payload inline reference.
2. **Versioning**: additive fields preferred; breaking changes use new event name or version bump with a dual-publish window documented for consumers.
3. **Interceptor ordering**: list interceptors in execution sequence (e.g. validate → enrich → serialize → emit on produce side; deserialize → auth → idempotency → handler on consume side). Document side effects each may add.
4. **Ordering guarantees**: state partition key rules and whether strict ordering is per-entity or best-effort; call out non-commutative handlers.
5. **Backpressure policy**: choose block, bounded buffer with drop-oldest/newest, sample, or shed load; tie each to SLAs and monitoring signals.
6. **Failure paths**: dead-letter topic or quarantine, retry with cap, poison-message handling; ensure event ids support idempotent retries.

## Output format

- **Envelope spec**: field table with type, required, and migration notes.
- **Interceptor diagram or ordered list**: names, responsibilities, failure behavior.
- **Load policy**: table of scenarios (normal, 2x burst, consumer stalled) → chosen behavior and metrics to watch.

## Gotchas

- Large payloads belong in object storage with a pointer in the envelope; streaming the blob inline can clog brokers.
- Idempotency keys must survive retries at every consumer, not only the first hop.
- Reordering interceptors can break auth if validation assumed an earlier step stripped fields.

## Test scenarios

1. **Schema bump**: New optional field added; spec should allow old consumers to ignore it and new consumers to read it without a flag day.
2. **Interceptor swap**: Metrics middleware moved after serialization; design should flag broken access to raw object and correct order.
3. **Consumer lag**: Queue depth grows tenfold; policy should define when to block producers vs drop vs scale consumers, with observable thresholds.
