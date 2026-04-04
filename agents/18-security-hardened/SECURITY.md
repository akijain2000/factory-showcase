# Security: Security-Hardened Agent

## Threat model summary

1. **Control disabling** — Users, compromised hosts, or prompts instruct disabling sanitization, injection detection, permission checks, or output validation.
2. **Policy bundle tampering** — Unsigned or stale `SECURITY_AGENT_POLICY_BUNDLE_REF` grants excessive tools or weakens rules fleet-wide.
3. **Audit sink failure or spoofing** — Missing evidence impairs forensics; forged audit rows obscure abuse.
4. **Bypass via ambiguous or dual-use content** — Content passes sanitizer but triggers privileged tools through social engineering in `check_permissions` scope.
5. **Schema and validator weakness** — `validate_output` gaps allow structured exfiltration or unsafe payloads that appear “valid.”

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| Raw user input | Critical | Untrusted; primary ingress. |
| `sanitize_input` / `detect_injection` | High | Must be invoked consistently; profile trade-offs (`SECURITY_AGENT_INJECTION_MODE`). |
| `check_permissions` | Critical | Enforces least privilege; integration bugs are catastrophic. |
| Inner agent + allowlisted tools | High | Bounded but still LLM-driven. |
| `SECURITY_AGENT_AUDIT_SINK_REF` | High | Integrity and availability of evidence. |
| Policy bundle delivery | High | Supply chain and rotation path. |

## Mitigation controls

- **HITL** for any request to disable or bypass security controls; no conversational override (see system prompt).
- **Signed bundles**, key rotation, and integrity alerts on `POLICY_INTEGRITY_FAIL`.
- **Append-only** audit sink with tamper-evident chaining; monitor for write failures and fail-closed where policy requires.
- **Automated tests** for injection cases and permission matrix; schema registry pinned by version.
- Separate **break-glass** roles with expiry and mandatory audit reason codes.

## Incident response pointer

Invoke **SOC / security engineering** on suspected policy tamper, repeated denials on privileged tools, or audit sink outages. Roll back policy bundle, block releases if fail-closed mode applies, and correlate `audit_log` ids with incidents. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | User content under legal hold, credentials | Minimize in audit; fingerprint only where required. |
| **Confidential** | Policy bundles, permission decisions, scan summaries | Internal; encrypted at rest; strict ACLs. |
| **Internal** | Reason codes, tool ids, principal ids | Standard security ops access. |
| **Public** | None assumed | Do not publish policy internals. |

## Compliance considerations

This agent is often deployed for **regulated** workloads: map controls to frameworks (e.g. SOC 2, ISO 27001, HIPAA technical safeguards). **Audit retention** must meet legal and contractual minimums. **Human oversight** may be required for high-risk automated decisions.
