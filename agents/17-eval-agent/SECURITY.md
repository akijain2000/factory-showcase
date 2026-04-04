# Security: Eval Agent (Adaptive Rubrics)

## Threat model summary

1. **Rubric calibration drift** — Large shifts in scores (>20% relative to baseline) hide quality regressions or manipulate release gates without detection.
2. **Trajectory data exposure** — Scoring prompts echo PII, secrets, or confidential content from `EVAL_AGENT_TRAJECTORY_STORE_REF` into logs or judge models.
3. **Registry tampering** — Unauthorized changes to rubric weights or revisions after scoring starts enable retroactive “pass” without re-run.
4. **Judge model manipulation** — Adversarial trajectory text or prompt injection biases `score_trajectory` outcomes.
5. **Anchor poisoning** — Compromised `anchor_trajectories` skew `calibrate_rubric` and downstream compliance claims.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `EVAL_AGENT_TRAJECTORY_STORE_REF` | High | Read access to sensitive behavioral data. |
| `EVAL_AGENT_RUBRIC_REGISTRY_REF` | High | Versioned contract for quality and safety gates. |
| `generate_rubric` / `calibrate_rubric` | Medium–High | LLM outputs become normative until challenged. |
| Scoring model endpoint | Medium | Third-party or shared processor of customer content. |
| Batch reports and aggregates | Medium | May re-identify users if trajectory refs are reversible. |

## Mitigation controls

- **HITL** for calibration that moves aggregate scores beyond policy thresholds; require dual review for safety-related dimensions.
- **Redaction profiles** on trajectories; minimize excerpts sent to judges; log `rubric_id` / span ids, not raw user text, by default.
- **Immutable rubric revisions**; new revision id for any weight change; re-score policy for production gates.
- Separate **producer vs judge** endpoints where policy requires; monitor for **self-grading** bias.
- Protect anchor sets with **access control** and integrity checks (hash pinned in registry).

## Incident response pointer

If calibration or rubric drift is suspected: **freeze** promotion using eval outputs, pin jobs to prior `rubric_revision`, preserve batch artifacts and anchor set hashes, and rerun with independent judges if needed. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Trajectories with PII | Often should not be scored; redact or exclude. |
| **Confidential** | Rubric text, scores, rationales | Internal; encrypted registry and report store. |
| **Internal** | Cohort ids, aggregate statistics | Standard ML platform controls. |
| **Public** | None by default | Publishing benchmarks needs legal clearance. |

## Compliance considerations

Evaluations over personal or sensitive behaviors may need **legal basis**, **DPIA**, and **human oversight** for automated decisions affecting individuals. Retention of trajectories and scores should match **records** and **privacy** schedules. Document **model processing** for subprocessors.
