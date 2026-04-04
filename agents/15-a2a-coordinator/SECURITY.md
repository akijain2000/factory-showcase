# Security: A2A Coordinator Agent

## Threat model summary

1. **Delegation to untrusted agents** — Tasks sent to peers with insufficient authentication, wrong trust tier, or malicious implementations leak `inputs_ref` or poison merged answers.
2. **Policy gate bypass** — `delegate_task` skips `POLICY_GATE_REF` checks, causing cross-zone exfiltration or regulated data on public-tier workers.
3. **Protocol and schema attacks** — Mismatched or downgraded protocols drop encryption, logging, or idempotency guarantees; confused-deputy at the message bus.
4. **Token and credential misuse** — Long-lived secrets passed to peers instead of short-lived scoped tokens; replay of `task_handle` or idempotency keys.
5. **Conflict resolution manipulation** — Forged or biased `collect_results` branches steer `resolve_conflicts` toward attacker-favored outcomes.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `AGENT_DIRECTORY_URI` | High | Spoofed capabilities if directory is not integrity-protected. |
| `A2A_MESSAGE_BUS_REF` | High | All delegated payloads transit here. |
| `POLICY_GATE_REF` | Critical | Must be invoked before enqueue. |
| `delegate_task` / `collect_results` | High | Data plane and result integrity. |
| `DELEGATE_TOKEN_ISSUER_REF` | High | Compromise enables arbitrary delegation as trusted workers. |

## Mitigation controls

- **HITL or automated trust checks** before delegating to untrusted agents (see system prompt).
- Enforce **mTLS/OAuth**, capability versioning, and **data classification** on every `delegate_task`; default deny cross-tier.
- Use **vault-scoped ephemeral tokens** only; never pass long-lived secrets in payloads.
- Sign or attest **directory entries**; monitor for unexpected peer registrations.
- Structured **provenance map** on every answer; escalate to human on `POLICY_DENY` or ambiguous conflicts.

## Incident response pointer

On suspected peer compromise: **revoke delegate tokens**, disable affected directory entries, quarantine partial aggregates by `correlation_id`, and notify peer owners. Preserve bus logs and protocol ids. See README **Rollback guide** for canceling downstream work.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | `inputs_ref` to regulated or customer data | Policy gate + peer tier match; minimal fields in messages. |
| **Confidential** | Full task specs, merge outputs | Internal; encrypt on bus where supported. |
| **Internal** | Protocol ids, task handles, SLA metadata | Standard ops access. |
| **Public** | None assumed | Do not publish delegation graphs with customer context. |

## Compliance considerations

Cross-agent flows must satisfy **DPA/subprocessor** lists, **data residency**, and **minimum necessary** sharing. Log **who delegated what** to which peer for audit. Multi-party AI may trigger **vendor risk** assessments for each registered agent.
