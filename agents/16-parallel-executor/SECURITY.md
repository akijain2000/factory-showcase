# Security: Parallel Executor Agent

## Threat model summary

1. **Resource exhaustion via fan-out** — Excessive concurrent shards (`>10` or beyond policy) causes CPU/memory saturation, quota burn, or downstream API abuse.
2. **Cross-shard data leakage** — Shared worker pools or merged artifacts mix tenant data when `correlation_id` or shard isolation fails.
3. **Malicious branch payloads** — Shards invoke privileged tools with attacker-controlled `payload`, enabling lateral movement or secret extraction.
4. **Trace and merge integrity** — Tampered `trace_aggregate` or `fan_in` ordering hides failures or injects false success signals.
5. **Retry and idempotency abuse** — `handle_partial_failure` retries amplify side effects (duplicate charges, duplicate writes) when child work is not idempotent.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `fan_out` / shard definitions | High | Arbitrary parallel tool invocation surface. |
| `set_concurrency_limit` | High | Raising limits without approval is a DoS/spend vector. |
| `PARALLEL_EXECUTOR_QUEUE_REF` / workers | High | Shared execution environment across tenants if not partitioned. |
| `PARALLEL_EXECUTOR_TRACE_STORE_REF` | Medium–High | May contain arguments, PII, and secrets from children. |
| `fan_in` / merge strategies | Medium | Logic bugs can drop security-relevant failure signals. |

## Mitigation controls

- Enforce **hard caps** on concurrent shards; **HITL** for execution above policy thresholds (see system prompt).
- **Tenant-scoped** queues and credentials per branch; never reuse output buffers across tenants.
- Require **allowlisted tools** per shard class; scan payloads for secret patterns before dispatch.
- **Immutable trace** append with `correlation_id` for audit; restrict trace store ACLs.
- Document **idempotency** requirements for each child tool; cap `PARALLEL_EXECUTOR_RETRY_ATTEMPTS` for side-effecting shards.

## Incident response pointer

On runaway fan-out or suspected cross-tenant merge: **halt dispatcher**, drain queue for the affected `correlation_id`, preserve traces, and lower concurrency before partial replay. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Shard payloads with PII, session tokens | Encrypt trace store; redact logs. |
| **Confidential** | Full merge outputs, tool responses | Internal-only; minimize retention. |
| **Internal** | Correlation ids, shard status rollups | Standard platform controls. |
| **Public** | None assumed | Do not export traces without review. |

## Compliance considerations

Parallel processing of personal data may require **purpose limitation** and **retention** on trace stores. Prove **isolation** between tenants for audits. High concurrency may trigger **provider rate** and **contractual** limits—document in DPIA and vendor reviews.
