# Security — Docs Maintainer Agent

## Threat model summary

1. **Cross-site scripting (XSS) via doc content** — Malicious Markdown, HTML, or MDX components render in the doc site or IDE preview and execute in readers’ browsers.
2. **Link hijacking** — Legitimate-looking URLs are swapped for phishing, malware, or token-grabbing endpoints; short links obscure destinations.
3. **Doc poisoning with false information** — Subtle edits to runbooks, security guidance, or API contracts mislead engineers into unsafe operations or wrong compliance posture.
4. **Path traversal in doc updates** — File write tools target `../../` paths or symlinks to overwrite code, CI configs, or secrets outside the docs tree.
5. **Social engineering via doc changes** — Urgent “run this curl” or “paste this key” instructions impersonate official process to compromise operators.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Authoring prompts and tickets** | Untrusted instructions to change docs. |
| **Markdown / MDX / HTML sources** | Raw HTML, script tags, `onerror`, custom components. |
| **Embedded assets and includes** | Transclusion pulls in untrusted fragments. |
| **PR and publishing pipelines** | Bots with commit access; static site generators with unsafe plugins. |
| **Search and preview UIs** | Client-side rendering without sanitization increases XSS blast radius. |

## Mitigation controls

- **Sanitization:** Use a strict allowlist for HTML; disable raw HTML in user-facing Markdown where possible; CSP on doc sites (`default-src 'self'`); encode output in preview tools.
- **Link policy:** Lint for unexpected domains; forbid `javascript:` and `data:` URLs; expand short links in CI for review; require HTTPS for external links in security-sensitive sections.
- **Integrity:** Mandatory human review for security/runbook/docs under `SECURITY*`, `CONTRIBUTING`, and incident paths; CODEOWNERS; diff size and path allowlists for automation.
- **Path safety:** Same root-jail and symlink controls as file-editing agents; block writes outside `docs/` (or configured roots); signed commits optional.
- **Training:** Style guide prohibiting inline scripts and credential examples; use placeholders and secret-scanning in CI.

## Incident response

1. **Contain:** Revert malicious commits; take affected doc versions offline or mark as compromised; invalidate CDN caches.
2. **Assess:** Review access logs for XSS exploitation; grep history for injected links and traversed paths; check whether readers executed harmful instructions.
3. **Notify:** If XSS affected authenticated doc portals, notify users and regulators per GDPR if personal accounts or tokens were at risk; customer comms if docs are customer-facing.
4. **Recover:** Patch sanitization and CSP; restore known-good content from backups; rotate credentials if runbooks led to disclosure.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| Public product docs | Public | Still subject to integrity and brand risk. |
| Internal runbooks | Confidential | Reveal architecture and incident procedures. |
| Security and compliance docs | Highly confidential | Direct impact if poisoned. |
| Preview / draft branches | Internal | May preview unreleased features. |

## Compliance considerations

- **GDPR:** Authenticated doc portals may hold personal data in examples or access logs; lawful basis and security of processing apply; breach if XSS steals sessions.
- **SOC 2:** CC7 for monitoring doc repo changes; CC8 for change management on customer-facing policies; CC6 if docs tie to access control decisions.
- **Accessibility / industry:** **WCAG** and sector regulators (e.g. **FDA** labeling) care about accurate public docs—poisoning can create secondary legal exposure beyond pure infosec.
- **SOC 2 / ISO 27001:** Document control procedures should mirror policy; automated editors must not bypass document approval workflows where required.

This document is guidance for deployments; it is not legal advice.
