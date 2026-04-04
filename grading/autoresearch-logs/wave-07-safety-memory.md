# Wave 7: Safety + Memory — Learning Log

**Date:** 2026-04-04  
**Target dimensions:** AGENT_SPEC dim 4 (Safety) + dim 5 (Memory)  
**Baseline:** Mean ~6.0/10 on safety (some constraints existed), ~4.0/10 on memory (no strategy docs)

## What was done

Added to all 20 agents:
- SECURITY.md: threat model, attack surface, mitigations, incident response, data classification, compliance
- Memory strategy in README: ephemeral vs durable state, retention, redaction, schema migration
- HITL gates in system-prompt.md: operations requiring human approval, approval flow, timeout behavior
- Domain-specific HITL examples (DB admin: DDL approval, security agent: control disablement approval, etc.)

## What INCREASES score (learnings)

1. **Domain-specific threat models** — Generic "injection is bad" scores poorly. A file organizer needs path traversal and symlink attack modeling. A knowledge graph agent needs entity resolution poisoning and graph cycle attacks. Specificity shows understanding.
2. **HITL gates with timeouts** — The most production-critical safety feature. Without HITL, autonomous agents can execute destructive operations without oversight. The timeout behavior (what happens if human doesn't respond in 5 minutes) is often overlooked.
3. **Data classification tables** — Labeling data by sensitivity (public, internal, confidential, restricted) enables proper access controls and audit trails.
4. **Memory redaction rules** — Explicitly stating "never persist PII, API keys, or credentials in durable state" prevents data leakage. This is a compliance requirement (GDPR, SOC2).
5. **Incident response pointers** — Security incidents with AI agents are novel. Having a contain → assess → notify → recover playbook specific to each agent type is valuable.
6. **Schema migration for memory** — When memory format changes between versions, agents need a migration strategy. Without this, upgrading an agent can corrupt its durable state.

## What DECREASES score (anti-patterns found)

1. **No security documentation** — Agents without SECURITY.md are treated as having no security considerations. This is the baseline for 6 of the 20 agents before this wave.
2. **No memory strategy** — Without explicit ephemeral/durable distinction, agents may persist sensitive data indefinitely.
3. **HITL without timeout** — If the approval flow has no timeout, the agent hangs forever waiting for human approval. This causes service outages.
4. **Generic compliance notes** — "We comply with regulations" is not useful. Specific references to GDPR Article 17 (right to erasure), SOC2 CC6.1 (logical access), etc. show real compliance understanding.
5. **Missing incident response** — Agents without IR pointers leave teams without a playbook when things go wrong.

## Metrics after Wave 7

- 20/20 agents: SECURITY.md with domain-specific threat models
- 20/20 agents: Memory strategy in README
- 20/20 agents: HITL gates in system-prompt.md
- Estimated dim 4 (safety): 9.0/10 (up from ~6.0)
- Estimated dim 5 (memory): 8.5/10 (up from ~4.0)
