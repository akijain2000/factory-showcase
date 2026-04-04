# Security — Incident Responder Agent

## Threat model summary

1. **Unauthorized production mutation** — Destructive runbook steps (restarts, deletes, config changes) without required human approval.
2. **Sensitive data in telemetry** — `query_logs` or diagnostics pulling PII, secrets, or customer content into model context, tickets, or pages.
3. **False escalation or alert fatigue** — Spurious `notify_oncall` / `create_incident` abuse or model loops paging engineers.
4. **Credential exposure in incidents** — Tokens or keys pasted into incident bodies or chat summaries.
5. **Attacker-driven reconnaissance** — Malicious operator or compromised account using read tools to map infrastructure.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Alert / operator input** | May be spoofed or poisoned to trigger wrong diagnostics. |
| **`check_health` / `query_logs` / `run_diagnostic`** | Broad read access to production; filters and redaction belong in tools. |
| **`notify_oncall` / `create_incident`** | Outbound comms; can leak data or harass on-call if misused. |
| **Autonomous step budget** | Limits damage but must be enforced in code, not only in prose. |
| **Session and audit logs** | Aggregate sensitive timelines; access-controlled storage required. |

## Mitigation controls

- **Default-deny destructive remediation** — README safety: allowlist per environment; human approval for high blast-radius actions.
- **Bounded autonomy** — `max_autonomous_steps`, circuit breakers, and stop after repeated failures (`system-prompt.md`).
- **Redaction** — Scrub PII from log excerpts and ticket bodies before model or pager; classify on-call messages as confidential.
- **Least privilege** — Read-only service accounts for telemetry; short-lived tokens for ticketing APIs.
- **Separation** — Route prod vs staging tools differently at the gateway.

## Incident response pointer

1. **Contain:** Disable mutating tools at the gateway; stop the agent session if it is amplifying an attack or leaking data.
2. **Assess:** Use `audit_log` / `mutation_log` and platform audit trails to list notifications and tickets created.
3. **Correct:** Update or close erroneous incidents; send follow-up to on-call through approved channels only.
4. **Escalate:** If auth anomalies or data integrity issues were observed, engage security incident command per org playbook (separate from this agent’s runbooks).

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|--------|
| Metrics and health summaries | Internal / confidential | May reveal architecture and load. |
| Log excerpts and trace IDs | Confidential | Often contain PII or session tokens if not redacted. |
| Incident tickets and pages | Confidential | Operational and sometimes customer-identifying. |
| Runbook and hypothesis text | Internal | May reference vulnerabilities—restrict distribution. |

## Compliance considerations

- **GDPR:** Log and ticket content may include personal data; define retention, lawful basis, and DPA with observability vendors.
- **SOC 2:** CC2 (communication), CC7 (monitoring), CC8 (change) align with controlled automation, approvals, and evidence in tickets.
- **HIPAA:** If monitors touch PHI-containing systems, BAA-covered tooling and minimum necessary log access are required.

This document is guidance for deployments; it is not legal advice.
