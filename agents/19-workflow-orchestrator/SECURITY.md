# Security: Workflow Orchestrator Agent

## Threat model summary

1. **Production data mutation via DAG steps** — `execute_step` runs writes, deletes, or migrations against production stores without human approval or dry-run.
2. **Checkpoint and output tampering** — Altered `WORKFLOW_CHECKPOINT_REF` contents replay wrong branches or skip compensating actions.
3. **Malicious or LLM-generated DAGs** — `define_dag` introduces cycles, privilege escalation steps, or data exfiltration nodes that pass weak schema validation.
4. **Condition injection** — Unsafe `expression_ref` or poisoned **facts** skip safety-critical steps or force destructive paths.
5. **Tenant bleed in executor** — Shared `WORKFLOW_EXECUTOR_REF` applies wrong `run_id` / `step_id` scoping, mixing customer data.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `define_dag` / planner LLM | High | Untrusted graph proposals until validated. |
| `execute_step` | Critical | Arbitrary side effects per worker implementation. |
| `WORKFLOW_CHECKPOINT_REF` | High | Durability + confidentiality of step outputs. |
| `evaluate_condition` | Medium–High | Branch decisions drive safety-critical paths. |
| `resume_from_checkpoint` | Medium | Replay can duplicate effects if idempotency fails. |

## Mitigation controls

- **HITL** (or enforced pipeline policy) for steps tagged **production data mutation**; require tickets and read-only previews first.
- **Schema + policy validation** on every DAG revision; static checks for forbidden tool/step types.
- Encrypt checkpoints **at rest**; strict tenancy on keys; signed `output_ref` where supported.
- Allow only **compiled expression refs**—no string eval from user text.
- **Idempotency** contract documented per step; monitor `retry_attempt` anomalies.

## Incident response pointer

Stop the **run_id**, preserve checkpoint snapshot and `WORKFLOW_AUDIT_REF` (if enabled), and avoid editing graphs for in-flight runs—start new **revision**. Roll back worker config if a bad step shipped. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Step outputs with PII, production row snapshots | Encrypted checkpoints; tight ACLs; minimal audit payloads. |
| **Confidential** | DAG definitions, branch decisions | Internal; version control with access reviews. |
| **Internal** | run_id, step status, hashes | Standard automation platform controls. |
| **Public** | None assumed | Do not publish workflow internals. |

## Compliance considerations

Workflows touching personal data need **logging of processing activities**, **retention** on checkpoints, and **access reviews** for who can resume or replay runs. **Segregation of duties** between DAG authors and production executors may be required. Document **subprocessors** invoked by worker steps.
