# Security — Learning Tutor Agent

## Threat model summary

1. **Cross-learner data access** — `recall_history` or memory backends returning another learner’s episodic or semantic records.
2. **PII and child data mishandling** — Names, emails, exact scores, or safeguarding-related content stored or logged inappropriately.
3. **Prompt injection via learner messages** — Attempts to extract rubrics, other users’ data, or override pedagogy/safety rules.
4. **Integrity of progress data** — Tampered `store_progress` or `assess_knowledge` outputs affecting grading or placement if integrated with LMS.
5. **Third-party model disclosure** — Session content sent to external LLM APIs without FERPA/COPPA-aligned agreements.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Learner messages** | Untrusted; may include PII or social-engineering against the tutor. |
| **`assess_knowledge` / `store_progress` / `recall_history`** | Read/write to durable stores; tenant and `learner_id` scoping is critical. |
| **`generate_exercise`** | Could emit inappropriate content if policies are weak; curriculum bounds needed in host. |
| **Semantic / episodic backends** | Compromise or misconfiguration leaks learning profiles across tenants. |
| **Logs and `mutation_log`** | May capture prompts and tool payloads; retention must match policy. |

## Mitigation controls

- **Isolation:** Strict `learner_id` (and tenant) checks in every tool handler; deny cross-learner reads.
- **Prompt rules:** No disclosure of internal keys, other learners’ data, or fabricated tool results (`system-prompt.md`).
- **PII minimization:** Prefer anonymized profiles in durable memory; redact before persistence per security constraints in system prompt.
- **Safeguarding:** Refusal and escalation paths for self-harm, abuse, or clinical overreach; human escalation mandatory.
- **Operational:** Encrypt stores at rest; BAAs/DPAs with model vendors when regulated learners are in scope.

## Incident response pointer

1. **Contain:** Disable `store_progress` writes; block affected `learner_id` sessions if breach is active.
2. **Assess:** Query `mutation_log` and backend stores for improper reads/writes; check audit trails for cross-tenant access.
3. **Notify:** FERPA/COPPA/GDPR obligations may require school, parent, or authority notification depending on jurisdiction and data exposed.
4. **Recover:** Tombstone or correct bad progress records; restore from last known good mastery snapshot from LMS.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|--------|
| Learner messages and emotional cues | Confidential / special category in EU | May include health or welfare signals. |
| Mastery and attempt history | Confidential | Educational records in many jurisdictions. |
| Semantic curriculum graph | Internal | Lower sensitivity unless tied to individuals. |
| Audit / mutation logs | Audit | May still contain sensitive snippets—minimize. |

## Compliance considerations

- **GDPR:** Children’s data and special-category inferences may trigger heightened protections and parental/guardian rights.
- **SOC 2:** CC6/CC7 for access to learning stores and logging; subprocessors for LLM APIs must be listed.
- **FERPA / COPPA (US):** **Highly applicable** in K–12 and under-13 contexts; institutional agreements and parental consent may be required; agent does not automate compliance—organizational controls required.
- **HIPAA:** Generally not applicable unless tutoring content intersects clinical or PHI workflows.

This document is guidance for deployments; it is not legal advice.
