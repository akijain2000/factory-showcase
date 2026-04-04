# Security: Self-Improver Agent (Autoresearch Harness)

## Threat model summary

1. **Safety constraint regression** — Edits to the inner prompt remove or weaken refusal rules, tool policies, or PII handling while metrics still “pass” a narrow suite.
2. **Eval sandbox escape or data misuse** — `run_evaluation` pointed at production/customer data or an overly permissive `EVAL_RUNNER_ENDPOINT` enables exfiltration or code execution.
3. **Suite gaming** — Changing fixtures, graders, or suite scope without governance to obtain favorable `compare_metrics`.
4. **Registry and artifact tampering** — Unauthorized `commit_or_revert` or tampered `PROMPT_REGISTRY_URI` / `METRICS_STORE_URI` breaks reproducibility and injects malicious prompts.
5. **Secret embedding in prompts** — Accidental inclusion of API keys or credentials in `edit_prompt` diffs, later promoted to production.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `edit_prompt` / `commit_or_revert` | Critical | Direct mutation of deployed behavior. |
| `EVAL_RUNNER_ENDPOINT` | Critical | Arbitrary code / network if misconfigured. |
| `EVAL_SUITE_REF` and fixtures | High | Integrity of benchmarks is security-relevant. |
| `PROMPT_REGISTRY_URI` / `METRICS_STORE_URI` | High | Long-lived persistence and audit evidence. |
| Outer harness LLM | Medium | Untrusted until gated; can propose unsafe diffs. |

## Mitigation controls

- **Freeze suite hash** per run; require ticketed approval for suite changes; network-restrict the eval runner.
- **Gates on primary safety metrics** and human review for any diff that touches safety/PII/tool policy sections (see system prompt HITL).
- Separate **experiment vs production** namespaces; dual-control on promotion to prod registry.
- Scan diffs for **secrets** before eval; block commits on pattern matches.
- Immutable **artifact storage** for eval outputs with signed metadata.

## Incident response pointer

If a bad prompt ships: **immediately revert** registry to prior version, invalidate cached prompts in runtimes, and preserve `run_id` / `candidate_id` / suite hash for forensics. See README **Rollback guide**. Escalate sandbox anomalies to security engineering.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Trajectories with PII (must not enter sandbox) | Synthetic/licensed fixtures only; redact exports. |
| **Confidential** | Prompt bodies, metrics, unified diffs | Internal; encrypted registry; access logging. |
| **Internal** | Suite version, seeds, aggregate scores | Standard R&D controls. |
| **Public** | None by default | Do not publish benchmarks without legal review. |

## Compliance considerations

Regulated orgs need **change management** for prompt updates, **segregation of duties** between author and approver, and **retention** policies for eval artifacts. Ensure **no production personal data** in eval unless contractually permitted. Document **model and data processing** for DPIA-style reviews.
