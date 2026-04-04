# Security — Migration Planner Agent

## Threat model summary

1. **SQL injection in generated migrations** — Dynamic string concatenation or unsafe quoting in emitted SQL allows attacker-controlled schema or data manipulation at apply time.
2. **Data loss from bad rollback** — Down migrations drop columns or tables without backup semantics, causing irreversible loss or corruption.
3. **Privilege escalation via DDL** — Generated scripts grant `SUPERUSER`, `SECURITY DEFINER`, dangerous extensions, or broad `GRANT`s that expand database trust.
4. **Schema enumeration** — Planner or connected tools leak full catalog metadata to unauthorized actors or external LLM contexts.
5. **Migration ordering attacks** — Reordered, duplicated, or conflicting versions skip security fixes or reintroduce vulnerable schema states.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Natural-language requirements** | Untrusted; may push toward destructive or over-privileged DDL. |
| **Existing schema inputs** | Dump files, live connections, or ORM models may be stale or malicious. |
| **Generated SQL / migration files** | Becomes executable in CI/CD and DBA workflows. |
| **Migration runners and credentials** | High-privilege DB roles; CI secrets. |
| **Collaboration channels** | Paste of full schemas may expose PII patterns or proprietary design. |

## Mitigation controls

- **Parameterized patterns:** Generate migrations via structured templates or ORM APIs that bind identifiers safely; forbid raw user text in executable SQL; static analysis on output for `EXEC`, `COPY PROGRAM`, extensions, and broad grants.
- **Least privilege:** Use migration-specific DB roles with minimal rights; separate read-only planning connections from apply roles; human approval for privilege-changing DDL.
- **Safety rails:** Require backups or snapshot gates before destructive ops; default to expand-contract patterns; block automatic `DROP DATABASE` / `TRUNCATE` without explicit flags.
- **Version integrity:** Signed or checksum-tracked migration ordering; CI checks for duplicate versions; peer review for all prod-bound files.
- **Data handling:** Redact or sample schemas for LLM context; avoid sending production row data; use synthetic names when demonstrating plans.

## Incident response

1. **Contain:** Stop migration pipelines; block apply of suspect versions; put affected databases in read-only or maintenance mode if corruption is suspected.
2. **Assess:** Diff applied vs expected migration history; query audit logs for unexpected DDL; identify data loss scope from rollback/forward failures.
3. **Notify:** Data loss or unauthorized schema change may trigger GDPR breach processes, customer SLAs, and SOC 2 customer communication clauses.
4. **Recover:** Restore from PITR or backups; replay clean migrations; rotate DB credentials if escalation occurred; document root cause for change control.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| Full schema dumps | Confidential / trade secret | Reveals product internals and integrations. |
| Migration SQL files | Highly sensitive | Executable; equivalent to production access in many setups. |
| Connection strings and roles | Restricted | Credentials and privilege maps. |
| LLM prompts containing schema snippets | Confidential | Third-party retention policies apply. |

## Compliance considerations

- **GDPR:** Schema and migrations may enable identification of data subjects; document processing; ensure subprocessors handling prompts are contracted; breach assessment if migrations expose or delete personal data wrongly.
- **SOC 2:** CC8 change management for database DDL; CC6 for production DB access; CC7 for logging of migration apply events.
- **PCI DSS:** **In scope** if migrations touch CDE databases; segregation of duties and audit trails for schema changes.
- **SOX / ITGC:** Material systems require controlled migration paths, approvals, and evidence retention.

This document is guidance for deployments; it is not legal advice.
