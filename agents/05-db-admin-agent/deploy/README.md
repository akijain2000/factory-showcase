# Deploy: Database Admin Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `DB_ADMIN_DSN_REF` | yes | Vault path to DB credentials (split RO/RW roles) |
| `DB_ADMIN_ALLOWED_SCHEMAS` | yes | Comma list or JSON array of schemas |
| `DB_ADMIN_READ_ONLY` | yes | `true` disables mutating `query_db` paths |
| `DB_ADMIN_HITL_ENDPOINT` | yes* | *Required when `execute_ddl` enabled |
| `DB_ADMIN_SANDBOX_SCHEMA` | optional | Trial schema for safe experiments |

## Health check

- `GET /healthz`: agent process up.
- `GET /readyz`: can open read connection with RO user; HITL service reachable if DDL enabled.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| `query_db` timeout | 5–30s |
| `execute_ddl` lock timeout | Low default; escalate on contention |
| Concurrent sessions | Small (1–3) for DDL |

## Operational notes

- **Secrets:** never log DSNs; rotate RW credentials on compromise.
- **Break-glass:** separate role for `DROP DATABASE` class operations; keep off by default.
- **Auditing:** log every `execute_ddl` with `approval_id`, `idempotency_key`, and operator identity from HITL payload.
