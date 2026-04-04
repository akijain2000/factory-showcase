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

## Dockerfile skeleton

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# DB_ADMIN_DSN_REF, DB_ADMIN_READ_ONLY, HITL endpoint secrets, MODEL_API_KEY — inject via vault

USER nobody
CMD ["python", "-c", "print('Wire DB pool + HITL client; see src/agent.py')"]
```

Prefer distroless or hardened base after proving compatibility; ensure ODBC/JDBC drivers if needed via multi-stage build.

## Required secrets (summary)

| Secret / env | Purpose |
|--------------|---------|
| `DB_ADMIN_DSN_REF` | Resolve to RO/RW database credentials |
| HITL / ticketing token endpoint | Validate `approval_id` for `execute_ddl` |
| `MODEL_API_KEY` | Optional LLM assist (keep DDL approval human-gated) |

## Resource limits (reference)

| Resource | Recommendation |
|----------|----------------|
| CPU | 0.5–1 vCPU |
| Memory | 256–512 MiB |
| DB client timeouts | 5–30s for `query_db`; strict lock timeouts for DDL |

## Health check configuration

- `GET /healthz`: process up.
- `GET /readyz`: RO DB ping; HITL reachable when DDL enabled.

```yaml
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
```
