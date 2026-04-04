# Security — Research Assistant Agent

## Threat model summary

1. **Source poisoning** — Adversarial or SEO-gamed pages dominate retrieval so answers reflect false or harmful claims as if authoritative.
2. **Citation fabrication** — The model invents URLs, studies, or quotes that appear credible but do not exist or misrepresent sources.
3. **Data leakage in search queries** — User topics, PII, or trade secrets are sent to third-party search or indexing APIs and retained or logged by vendors.
4. **Prompt injection via retrieved content** — Malicious snippets in crawled pages instruct the model to ignore policies, exfiltrate context, or take unsafe follow-on actions.
5. **Sensitive data in memory / context** — Long sessions retain secrets, tokens, or regulated content in model context, caches, or tool backends without TTL or redaction.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **User queries and follow-ups** | Untrusted; may embed injection or exfiltration attempts. |
| **Web search / browse / fetch tools** | Outbound URLs and query strings; response HTML/JSON is untrusted. |
| **RAG corpora and embeddings** | Poisoned documents skew retrieval; stale indexes mislead. |
| **Model APIs and logging** | Prompts and completions may be stored by providers or host platform. |
| **Session and tool memory** | Cross-request retention increases disclosure window. |

## Mitigation controls

- **Retrieval hygiene:** Allowlist domains where possible; block `file://` and internal IP ranges for browse/fetch; use TLS and certificate validation; rate-limit and sandbox fetches.
- **Citation discipline:** Require verifiable links or corpus IDs; automated checks that URLs resolve and match quoted text where feasible; train/refuse when evidence is insufficient.
- **Injection defenses:** System prompts that treat retrieved text as data not instructions; delimiter wrapping; output-only responses from browse tools; no execution of code from pages.
- **Privacy:** Minimize query text sent to external search; use enterprise search endpoints with DPAs; redact PII before external calls; short context windows and explicit “forget” for sensitive threads.
- **Operational:** Disable training on customer data where offered; encrypt caches at rest; access controls on research corpora per tenant.

## Incident response

1. **Contain:** Disable browse/search tools for affected tenants; revoke compromised API keys; purge poisoned index segments if applicable.
2. **Assess:** Review prompts and retrieved URLs for injection patterns; determine whether false citations were acted on in downstream systems; check vendor access logs for query leakage.
3. **Notify:** If personal or regulated data was transmitted to subprocessors without authorization or disclosed in outputs, follow GDPR and contractual notification requirements.
4. **Recover:** Refresh RAG from trusted baselines; patch allowlists; communicate corrections to users who received poisoned answers.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| User research questions | Confidential | Often includes strategy, health, or legal topics. |
| Fetched web content | Untrusted / variable | Treat as malicious until normalized; do not persist raw HTML unnecessarily. |
| Search query logs | Confidential | May duplicate user PII or secrets. |
| Generated summaries with citations | Internal–Confidential | Becomes a new artifact; distribution rules apply. |

## Compliance considerations

- **GDPR:** Lawful basis for processing queries and web fetches; subprocessors (search, LLM) in RoPA; DPIA if large-scale monitoring of research topics; data subject rights on stored threads.
- **SOC 2:** CC6 for external API credentials; CC7 for logging and monitoring of tool use; vendor management for search/LLM providers.
- **CCPA / CPRA:** Disclosures if personal information is “sold” or shared with ad-tech adjacent search tools—prefer enterprise APIs without secondary use.
- **Industry-specific:** **FERPA**, **HIPAA**, or **export control** may restrict what may be searched or summarized; organizational policy must gate the agent.

This document is guidance for deployments; it is not legal advice.
