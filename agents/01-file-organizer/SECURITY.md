# Security — File Organizer Agent

## Threat model summary

1. **Path traversal** — User or upstream prompts supply `../` or encoded path segments so reads/writes escape the intended workspace root.
2. **Symlink attacks** — Operations follow symbolic links into sensitive system paths or other tenants’ directories, enabling read/write outside scope.
3. **File permission escalation** — Automated chmod/chown suggestions or tool misuse weakens ACLs or grants group/world access to confidential files.
4. **Data exfiltration via move** — “Organize” or batch move operations copy or relocate secrets, keys, or regulated data to attacker-controlled or world-readable locations.
5. **Denial of service via recursive listing** — Deep trees, cyclical symlinks, or huge directories exhaust CPU, memory, or API quotas.

## Attack surface analysis

| Surface | Manipulation risk |
|--------|-------------------|
| **Natural-language instructions** | Untrusted; may encode malicious paths or override safety rules. |
| **Path arguments to file tools** | Direct injection of traversal, UNC paths, or `file://` URLs depending on implementation. |
| **Glob / find / list operations** | Unbounded recursion or symlink loops; metadata-only vs content reads. |
| **Move, copy, rename, delete** | Integrity and confidentiality impact; cross-volume behavior. |
| **Host filesystem and mount namespaces** | Misconfiguration expands effective root beyond the intended sandbox. |

## Mitigation controls

- **Root jail:** Resolve all paths under a single configurable workspace root; reject `..` after canonicalization; optional `realpath` + prefix check; no follow for symlinks on sensitive ops or use `O_NOFOLLOW` patterns where the platform allows.
- **Quotas:** Cap depth, file count, and total bytes per listing or batch job; detect symlink cycles; timeout long scans.
- **Least privilege:** Run the agent OS identity with minimal filesystem permissions; separate service accounts per tenant; never suggest broad `chmod 777` or weakening ACLs without explicit human approval.
- **Secrets hygiene:** Blocklist known secret filenames (e.g. `.env`, `id_rsa`); warn before moving credential-bearing paths; scan diffs/logs for accidental moves of key material.
- **Audit:** Log path decisions (canonical path, action, actor, tenant); alert on traversal attempts and symlink escapes.

## Incident response

1. **Contain:** Halt file-organizer jobs; revoke or narrow host credentials; snapshot affected volumes if forensic preservation is required.
2. **Assess:** Review audit logs for abnormal paths, cross-tenant access, or mass moves; compare file hashes or backups for tampering or exfiltration.
3. **Notify:** If regulated or customer data left the trusted boundary, follow GDPR breach timelines, contractual SOC 2 / customer security clauses, and internal IR playbooks.
4. **Recover:** Restore from immutable backups; fix symlink and root configuration; rotate any credentials that may have been touched or exposed.

## Data classification

| Data | Typical sensitivity | Notes |
|------|---------------------|-------|
| Arbitrary user / repo files | Confidential to highly restricted | May include source, contracts, PHI, or credentials. |
| Path metadata and listings | Internal | Can still reveal structure and project names. |
| Agent logs with full paths | Confidential | May embed customer names or internal host layout. |
| Organized output manifests | Internal | Maps source to destination; treat as operational data. |

## Compliance considerations

- **GDPR / UK GDPR:** File contents may be personal data; processing needs lawful basis, DPA with subprocessors, and breach notification if personal data is exfiltrated or misplaced.
- **SOC 2 (CC6/CC7):** Logical access to filesystems, change management for automation that moves production assets, and logging of privileged file operations.
- **HIPAA / PCI:** **Highly applicable** when the workspace can contain PHI or cardholder data; scope the agent out of such paths or enforce BAA/PCI segmentation and monitoring.
- **ISO 27001:** Asset handling, media handling, and supplier controls for any hosted execution environment.

This document is guidance for deployments; it is not legal advice.
