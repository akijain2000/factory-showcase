# Security: Cost Optimizer Agent

## Threat model summary

1. **Budget and ledger manipulation** — Attacker or bug inflates allowances, deletes attribution, or writes false `track_tokens` rows to hide abuse.
2. **Circuit breaker bypass** — Instructions or config changes disable downgrade/halt paths, causing runaway spend or denial of service to tenants.
3. **Routing exfiltration** — Request metadata routed to unintended models or regions leaks prompts, PII, or IP across trust boundaries.
4. **Privilege abuse of `OPERATOR_OVERRIDE`** — Break-glass paths used routinely, defeating FinOps and safety caps.
5. **Pricing and route table tampering** — Stale or malicious `PRICING_TABLE_REF` / `MODEL_ROUTE_TABLE_REF` misleads estimates and audits.

## Attack surface analysis

| Surface | Exposure | Notes |
|--------|----------|--------|
| `BUDGET_LEDGER_URI` | High | Authoritative for spend; target for fraud and tampering. |
| `check_budget` / `route_to_model` | High | Gate every request; confused-deputy if caller identity is weak. |
| `track_tokens` / `estimate_cost` | Medium–High | Data integrity and cache poisoning affect billing and safety. |
| `CIRCUIT_BREAKER_POLICY_REF` | High | Direct control over halt/downgrade behavior. |
| Logs and attribution fields | Medium | May contain tenant ids, request metadata, prompt hashes. |

## Mitigation controls

- **Append-only** or compensating-entry ledger with strong auth; separate read vs write roles; monitor anomalous write rates.
- Enforce **tenant binding** on `check_budget` and `route_to_model`; deny when scope does not match authenticated principal.
- Protect pricing and route configs with **versioning, signatures, and CI**; short TTL on estimate caches after price changes.
- Restrict **`OPERATOR_OVERRIDE`** to time-bound, audited roles; alert on repeated override use.
- Log **decision ids** and hashes of prompts, not raw content, unless explicitly allowed.

## Incident response pointer

Treat ledger anomalies or breaker bypass as **FinOps + security** incidents: freeze routing changes, preserve ledger snapshots, revert `MODEL_ROUTE_TABLE_REF` / breaker policy to last known good, and reconcile usage with provider bills. See README **Rollback guide**.

## Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| **Restricted** | Prompt-linked attribution when content is sensitive | Hash/minimize; residency-aware ledger regions. |
| **Confidential** | Full routing decisions, tenant caps, breaker state | Internal FinOps and platform only. |
| **Internal** | Aggregated spend, request_id linkage | Standard access controls. |
| **Public** | None by default | Do not publish per-tenant usage. |

## Compliance considerations

Align with **contractual SLAs**, **SOX**-style controls if spend is material, and **privacy** rules when attribution ties to individuals. Maintain **audit trails** for cap changes and overrides. Cross-border routing must match **data residency** commitments for model providers.
