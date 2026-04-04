# Security — Database Admin Agent

## Threat model summary

1. **Unauthorized DDL or data writes** — `execute_ddl` or broad `query_db` without valid HITL approval or least-privilege DB role.
2. **Credential exposure** — DSNs, passwords, or tokens echoed in chat, logs, or error messages.
3. **SQL injection and unsafe dynamics** — Untrusted input concatenated into SQL despite parameterized tool contracts.
4. **Excessive data access** — SELECT queries returning large volumes of PII to the model or logs without masking.
5. **Approval token replay or forgery** — Fake `approval_id` values if ticketing integration is weak or client-trusted.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **User / operator messages** | May urge bypass of sandbox, HITL, or read-only profile. |
| **`query_db`** | Read path; in wrong profile could allow destructive statements if validation is naive. |
| **`explain_query`** | Can leak schema and statistics; still sensitive in multi-tenant settings. |
| **`backup_table` / `execute_ddl`** | Mutations; require backup policy and HITL per deploy README. |
| **Session fields (`approval_id`, `last_backup_id`)** | Forgery or stale reuse if not validated server-side. |

## Mitigation controls

- **HITL for DDL:** Runtime-enforced approval tokens for `execute_ddl`; do not accept secrets pasted in chat (see `system-prompt.md`).
- **Read-only profile:** `DB_ADMIN_READ_ONLY` / `read_only_sql` with SELECT-only patterns for default operation.
- **Sandbox:** `DB_ADMIN_SANDBOX_SCHEMA` and server-side statement validation; block role/database switching where possible.
- **Parameterized queries:** Enforce `params` on `query_db` in implementations; reject concatenated untrusted input.
- **Backup-before-DDL:** Enable `require_backup_before_ddl` in production for critical tables.

## Incident response pointer

1. **Contain:** Revoke RW credentials; kill sessions; disable `execute_ddl` in the tool gateway.
2. **Assess:** Use DB audit trails and agent `audit_log` (with `approval_id`, operator identity) to scope changes.
3. **Recover:** Restore from `last_backup_id` / snapshots; apply corrective DDL from change tickets.
4. **Rotate:** Invalidate `DB_ADMIN_HITL_TOKEN` / approval workflow keys; review ticketing integration for replay.

Engage DPO/security if PII was extracted or disclosed.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|--------|
| Query results | Up to **highly confidential** | Often includes PII/PHI depending on database. |
| Explain plans and schema names | Confidential | Metadata about systems and scale. |
| Approval and backup identifiers | Confidential / audit | Tie to change management. |
| Connection configuration | Critical | Treat as secret at all times. |

## Compliance considerations

- **GDPR:** Database access to personal data requires lawful basis, access logging, and DPIA for high-risk processing; support erasure/portability at the DB layer.
- **SOC 2:** CC6 (access), CC7 (monitoring), CC8 (change) map directly to HITL, least privilege, and audit logs.
- **HIPAA:** **Highly applicable** when connected to PHI systems; requires BAAs, encryption, audit controls, and minimum necessary queries—agent must use masked responses in tools where required.

This document is guidance for deployments; it is not legal advice.
