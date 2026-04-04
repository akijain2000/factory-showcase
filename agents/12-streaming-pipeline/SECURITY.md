# Security: Streaming Pipeline Agent

## Threat model summary

1. **Malicious or forged producers** — Spoofed `producer_id` or synthetic events inject bad data, trigger mass cancellation, or exhaust consumers.
2. **Interceptor chain abuse** — Malicious or buggy interceptors exfiltrate payloads, disable audit/policy hooks, or run blocking work on the hot path enabling DoS.
3. **Topic and scope confusion** — Mis-scoped `cancel_subtree` or wrong partition keys cause cross-tenant leakage, data loss, or operational outages.
4. **Backpressure and queue exhaustion** — Adversarial emit rates or unbounded buffering lead to memory pressure and service degradation.
5. **Sensitive payloads on the bus** — PII or secrets in event bodies observable to interceptors, aggregates, and logs.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `EVENT_BUS_ENDPOINT` / producers | High | Ingress for unauthenticated or weakly authenticated traffic is critical risk. |
| `register_interceptor` / registry | High | Elevated access to all events on bound topics. |
| `emit_event` / `aggregate_stream` | High | Data plane; aggregation windows may retain sensitive state. |
| `cancel_subtree` | Medium–High | Destructive; scope bugs amplify impact. |
| `inspect_backpressure` and metrics | Medium | May leak operational fingerprints; samples can expose PII if not redacted. |

## Mitigation controls

- Authenticate and authorize **producers** at bus ingress; require provenance fields on `emit_event`.
- **Code review and signing** for interceptors; separate roles for register vs emit; rate limits per producer/topic.
- Enforce **payload size caps** and schema validation at ingress; default-deny unknown topics where appropriate.
- Restrict **root-level cancellation** to break-glass roles; require `reason_code` and audit all `cancel_subtree` calls.
- Redact **PII in audit hooks** and backpressure samples; minimize retention of aggregate buffers.

## Incident response pointer

For suspected forged traffic or interceptor compromise: **pause producers** for affected scopes, preserve broker offsets and registry versions, and review `causation_id` traces. See README **Rollback guide** for reverting interceptor order and recovery after cancel storms.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Events with PII, auth tokens, payment data | Encrypt in transit/at rest; minimal fields in aggregates; strict topic ACLs. |
| **Confidential** | Full event bodies, internal topology | Internal-only; redacted samples in ops views. |
| **Internal** | Lag metrics, scope ids, interceptor order | Standard monitoring access controls. |
| **Public** | None assumed | Do not publish raw streams. |

## Compliance considerations

Streaming systems often fall under **logging and monitoring** policies and, when PII is present, **data minimization** and **retention limits** for buffers and replays. Ensure **lawful basis** for processing and support **erasure** where event payloads identify individuals. Document **cross-border** replication if the bus spans regions.
