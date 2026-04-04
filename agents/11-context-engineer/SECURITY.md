# Security: Context Engineer Agent (ACE)

## Threat model summary

1. **Prompt-injection via curated corpora** — Adversarial or compromised traces persuade the agent to promote system text that weakens safety, exfiltrates data, or bypasses quality gates.
2. **Unauthorized prompt promotion** — An attacker or misconfigured host promotes draft prompts without review, causing fleet-wide behavior drift or policy violations.
3. **Context store integrity and tenancy** — Cross-tenant reads/writes, or tampering with `content_hash` / lineage, break auditability and enable data mingling.
4. **Sensitive data in bundles** — Customer PII, credentials, or regulated content persisted in curated windows without redaction.
5. **Compression and reflection abuse** — Lossy `compress_context` or biased `reflect_on_output` loops strip safety constraints or overfit to attacker-shaped failure modes.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| Ingested user/task text and traces | High | Untrusted; may contain instructions posing as content. |
| `CONTEXT_STORE_URI` and prompt registry | High | Durable; target for exfiltration, tampering, and lateral movement. |
| `update_system_prompt` / promotion APIs | High | Direct impact on model behavior across sessions. |
| `MODEL_API_ENDPOINT` | Medium | Prompts and context leave the boundary; provider compromise or logging matters. |
| Tool schemas and host callbacks | Medium | Confused-deputy if callers are not authenticated. |

## Mitigation controls

- Enforce **human or automated review** before promotion; require `dry_run` first and hash/version concurrency (compare-and-swap).
- Apply **`REDACTION_RULESET_REF`** (or equivalent) before persistence; block bundles that still contain secret patterns.
- Tag **immutable** constraints (safety, tool contracts) so compression cannot drop them without explicit policy.
- Isolate **`PROMPT_VERSION_NAMESPACE`** and context store by tenant; least-privilege credentials for store access.
- Log **session_id**, **bundle_id**, prompt **version**, and promotion decisions; avoid logging full prompts in production.

## Incident response pointer

Treat suspected prompt tampering or cross-tenant leakage as a **high-severity** incident. Follow your org IR playbooks: freeze promotion, roll back to last signed prompt version, preserve store snapshots and audit logs, and correlate tool spans with `session_id` / `bundle_id`. See README **Rollback guide** for operational undo steps.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Curated excerpts with customer PII, security incident content | Redact before store; encrypted store; strict ACLs. |
| **Confidential** | Full traces, draft prompt bodies, reflection notes | Internal-only; minimize retention; no public logging. |
| **Internal** | Quality scores, bundle metadata, version ids | Standard internal controls. |
| **Public** | None by default from this agent | Do not publish curated content without review. |

## Compliance considerations

Map retention of context and prompts to **records management** and **privacy** programs (e.g. purpose limitation, erasure on request where bundles identify individuals). Regulated environments may require **change control** and **segregation of duties** for prompt promotion. Ensure **cross-border** model inference and store regions align with data residency policy.
