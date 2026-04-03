# Database Admin Agent (Safety-Critical)

A **safety-critical** agent for **read-mostly** operations and **strictly gated** DDL. Every **destructive** or **schema-changing** path requires **human-in-the-loop (HITL)** approval enforced by the runtime, not merely suggested in prose.

## Audience

DBAs and platform engineers who want an LLM assistant that **cannot** bypass organization policy: least privilege, backups before DDL, and query explain-before-run patterns.

## Quickstart

1. Load `system-prompt.md`.
2. Wire tools in `src/agent.py` with **hard gates** (see `deploy/README.md`).
3. Start in **read-only** profile: only `query_db` (SELECT) and `explain_query` enabled.

## Configuration

| Variable | Description |
|----------|-------------|
| `DB_ADMIN_DSN_REF` | Vault reference to read/write credentials (separate RO user recommended) |
| `DB_ADMIN_HITL_TOKEN` | Approver-issued token consumed by `execute_ddl` |
| `DB_ADMIN_SANDBOX_SCHEMA` | Optional schema prefix for trial DDL |

## Architecture

```
 +----------------+       +-------------------+
 | User / ticket  |------>| DB Admin Agent    |
 +----------------+       | (policy + tools)  |
                            +---------+---------+
                                      |
            +-------------------------+-------------------------+
            |                         |                         |
            v                         v                         v
    +---------------+         +---------------+         +---------------+
    |   query_db    |         | explain_query |         | backup_table  |
    |  (SELECT-only |         | (plan + cost) |         | (pre-DDL snap)|
    |   in RO mode) |         +---------------+         +---------------+
    +---------------+                                           |
            \------------------------------------------------------+
                                      |
                                      v
                            +---------------+
                            | execute_ddl   | <--- HITL gate + backup id
                            +---------------+
                                      |
                                      v
                            +---------------+
                            |   Database    |
                            | (sandboxed)   |
                            +---------------+
```

## Safety layers

1. **Network / identity:** dedicated DB role with column/table grants.
2. **Sandbox:** optional schema; block `DROP DATABASE`, `TRUNCATE` unless explicit break-glass role.
3. **HITL:** `execute_ddl` requires valid approval payload from ticketing system.
4. **Backup:** `backup_table` (or snapshot) must precede risky DDL per policy.

## Testing

See `tests/` for HITL and read-only enforcement scenarios.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
