# Security — Support Triage Agent

## Threat model summary

1. **PII and credential exposure** — Ticket bodies, drafts, and KB snippets flowing to logs, LLMs, or wrong queues without redaction.
2. **Social engineering and account takeover assistance** — `generate_response` advising users to bypass security or share secrets.
3. **Wrong routing or automation harm** — Low-confidence or malicious input routed to self-serve with incorrect commitments.
4. **Cross-tenant leakage** — KB or ticket tools returning another customer’s articles or metadata.
5. **CRM mutation abuse** — `route_ticket` or integrations creating spam tickets or mis-prioritized incidents.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Ticket payload** | Untrusted; may contain malware links, injection, or pasted secrets. |
| **`classify_intent`** | Structured labels drive routing; manipulation affects downstream teams. |
| **`search_kb`** | Retrieval scope must be tenant/account aware. |
| **`route_ticket` / `generate_response` / `escalate_to_human`** | Write to customer-visible or internal systems; highest impact. |
| **Model and logs** | Full ticket text may be retained by providers; classify accordingly. |

## Mitigation controls

- **Routing rules:** Explicit table for security, P1, low confidence → human or security queue (`system-prompt.md`).
- **Redaction:** Passwords, API secrets, PANs → redact in replies and escalate; never echo full secrets.
- **Grounding:** KB/policy citations required before SLA or refund commitments; refuse when policy text is missing.
- **Governance:** Log `route_ticket` with ticket id and model version (README); human approval before sending drafts in high-risk profiles.
- **Tenant isolation:** Enforce account-scoped credentials and KB indices in tool implementations.

## Incident response pointer

1. **Contain:** Disable `generate_response` auto-send; pause routing for affected ticket IDs.
2. **Assess:** Reconstruct classification JSON and tool order from `sla_routing_log` / `audit_log`; identify mis-routed or leaked data.
3. **Notify:** GDPR breach assessment if personal data went to wrong recipient or unsecured channel; notify customers per contract.
4. **Correct:** Update CRM records; retract unsent drafts at the messaging gateway; retrain or patch routing rules in code.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|--------|
| Ticket subject/body | Confidential / personal data | Often PII and account detail. |
| KB snippets | Confidential | May include internal procedures. |
| Classification JSON | Internal | Reveals intent and sentiment modeling. |
| Draft replies | Confidential | Customer-facing; pre-send review recommended. |

## Compliance considerations

- **GDPR:** Support data is typically personal data; lawful basis, retention limits, subprocessors (LLM), and breach notification rules apply.
- **SOC 2:** CC6/CC7 for access to CRM and logging of automated decisions; CC2 for customer communication integrity.
- **HIPAA:** **Applicable** if helpdesk handles PHI (e.g., health SaaS); requires BAAs, minimum necessary in prompts/logs, and restricted auto-replies.

This document is guidance for deployments; it is not legal advice.
