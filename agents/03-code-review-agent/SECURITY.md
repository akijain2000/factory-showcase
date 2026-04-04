# Security — Code Review Agent

## Threat model summary

1. **Malicious code in PRs** — Review-time execution (CI, local checkout, or “helpful” suggested commands) triggers supply-chain or RCE payloads hidden in diffs.
2. **Secret leakage in diffs** — API keys, tokens, or customer data appear in patches; the agent echoes them into comments, logs, or external LLM backends.
3. **Privilege escalation via review bypass** — Adversarial PR text or comments coerce “LGTM” or weak findings, skipping required security or compliance gates.
4. **Code injection in review comments** — Markdown/HTML in bot comments executes in developer UIs (e.g. unsafe rendering) or tricks maintainers into pasting unsafe snippets.
5. **Supply chain attacks via dependencies** — Lockfile or manifest changes introduce typosquatted or compromised packages without adequate dependency review depth.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **PR title, description, comments** | Untrusted; prompt injection and social engineering. |
| **Diffs and patches** | Malicious content; binary blobs; huge files causing DoS. |
| **Repository metadata** | Branch names, commit messages, CI configs as attack channels. |
| **Review output channels** | Git hosting APIs, chat integrations, email—each has injection and retention risk. |
| **Tooling (git, linters, scanners)** | Parsing untrusted code; subprocess invocation if misconfigured. |

## Mitigation controls

- **Non-execution:** Never run code from the PR inside the agent’s trust boundary; rely on read-only diff ingestion; isolate any optional static analysis in disposable CI jobs with secrets stripped.
- **Secret scanning:** Pre-review secret detection on patches; redact findings in posted comments; block posting full matched secrets; rotate if leaked.
- **Policy gates:** Mandatory human or second-bot review for security-sensitive paths; deterministic checklist for auth, crypto, and dependency changes; refuse blanket approval language for high-risk diffs.
- **Safe rendering:** Escape or sanitize markdown in comments; no raw HTML; use CSP-safe viewers for integrated UIs.
- **Dependency focus:** Flag new transitive deps, install scripts, and postinstall hooks; link to advisory DBs; encourage pinned hashes.

## Incident response

1. **Contain:** Disable auto-merge or bot approvals; freeze PR if active exploitation suspected; revoke tokens if secrets appeared in comments or logs.
2. **Assess:** Scrub review history and LLM vendor logs for echoed secrets; scan merged commits for malware; review bypassed checks.
3. **Notify:** Inform security and affected teams; regulatory/customer notice if secrets or regulated code paths were exposed.
4. **Recover:** Rotate credentials; revert malicious merges; strengthen branch protection and required reviewers; add regression tests for the bypass pattern.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| Source code under review | Confidential / trade secret | Core IP; export-controlled in some orgs. |
| PR discussion | Internal–Confidential | May include vulnerabilities and customer names. |
| Diff artifacts in LLM logs | Highly restricted | Often equals full source; vendor handling matters. |
| Security scan outputs | Confidential | Reveals weaknesses; limit distribution. |

## Compliance considerations

- **GDPR:** Code and tickets may contain personal data (emails, IDs); subprocessors storing prompts need a DPA; minimize EU personal data in diffs sent externally.
- **SOC 2:** CC8 change management alignment; CC6 access to repos; CC7 monitoring of bot actions and admin overrides.
- **PCI / HIPAA:** If the repo touches in-scope systems, reviews must not leak cardholder or PHI into unsecured channels; scope separation is preferred.
- **Export / sanctions:** **EAR / ITAR** or similar may restrict sharing certain code with foreign-hosted LLMs—use regional or self-hosted models when required.

This document is guidance for deployments; it is not legal advice.
