# Security — API Test Generator Agent

## Threat model summary

1. **SSRF via test targets** — Generated tests call internal IPs, metadata endpoints, cloud control planes, or file URLs, pivoting from CI into private networks.
2. **Credential exposure in test configs** — API keys, OAuth client secrets, or JWTs are embedded in fixtures, env blocks, or committed artifacts.
3. **Code injection in generated tests** — Malicious payloads in OpenAPI examples or recorded traffic become executable test code (e.g. `eval`, dynamic `require`) when codegen is naive.
4. **Test environment escape** — Tests break out of containers through privileged mounts, docker.sock access, or overly broad host networking.
5. **API key harvesting** — Fuzzing or replay tests exfiltrate tokens from responses, logs, or shared mock servers.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **API specs, Postman collections, HAR files** | Untrusted input driving codegen and URLs. |
| **Base URL and environment variables** | Points tests at prod or internal services. |
| **Generated test source** | Executed in CI with secrets in scope. |
| **Mock servers and recorders** | May persist sensitive request/response bodies. |
| **Outbound HTTP from CI** | SSRF, data exfiltration, and abuse of third-party APIs. |

## Mitigation controls

- **Network policy:** Deny RFC1918, link-local, and metadata addresses unless explicitly allowlisted; use egress proxies; resolve and validate hostnames before requests; no raw IP literals from untrusted specs without review.
- **Secrets management:** Inject credentials via CI secret stores only; forbid literals in generated files; use short-lived tokens; scan repos for high-entropy strings.
- **Safe codegen:** Emit tests in a safe subset of the language; no dynamic code execution from spec strings; sanitize interpolated values; pin codegen libraries.
- **Isolation:** Run tests in dedicated low-privilege service accounts; disable docker.sock; read-only filesystem where possible; separate prod vs staging endpoints by enforced config.
- **Logging:** Redact `Authorization` headers and PII from test output; aggregate failures without echoing full secrets.

## Incident response

1. **Contain:** Stop CI pipelines running suspect generated tests; revoke exposed keys; block egress from affected runners.
2. **Assess:** Identify which internal URLs were hit; review artifacts and logs for leaked credentials; determine if prod data was accessed.
3. **Notify:** SSRF into customer networks or cloud accounts may require customer and regulator communication under GDPR, SOC 2, or contractual IR clauses.
4. **Recover:** Rotate all potentially exposed secrets; patch generator rules; re-run tests in hardened sandboxes; add regression cases for the failure mode.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| API specs and examples | Internal–Confidential | May describe unreleased products. |
| Recorded traffic (HAR) | Confidential | Often contains tokens and PII. |
| Generated tests | Internal | Executable; can embed sensitive endpoints. |
| CI logs | Confidential | Frequently leak redacted-but-present hints. |

## Compliance considerations

- **GDPR:** Test payloads and responses may contain personal data; limit retention in mocks; DPIA if large-scale real data is replayed; subprocessors for CI and LLM codegen need DPAs.
- **SOC 2:** CC6 logical access to CI secrets; CC7 monitoring for unusual egress; vendor risk for hosted runners.
- **PCI DSS:** **Highly applicable** if tests target or accidentally reach payment APIs; segmentation and PAN prohibitions in non-CDE test data are mandatory.
- **FedRAMP / ISO 27001:** Strong controls on SSRF and secret handling align with cloud security baselines.

This document is guidance for deployments; it is not legal advice.
