# Deploy: Context Engineer Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `CONTEXT_STORE_URI` | yes | Durable storage for bundles, reflections, and prompt metadata |
| `CONTEXT_MAX_TOKENS` | yes | Working context ceiling used by compression triggers |
| `PROMPT_VERSION_NAMESPACE` | yes | Isolated namespace for draft vs. production prompt revisions |
| `MODEL_API_ENDPOINT` | yes | Upstream inference endpoint for the agent’s own calls (credentials via host secret store) |
| `REDACTION_RULESET_REF` | recommended | Pointer to org redaction patterns for `curate_context` |

## Health and readiness

- **Liveness:** process responds within SLO; background summarization workers heartbeating.
- **Readiness:** `CONTEXT_STORE_URI` reachable; prompt registry readable; rate limits for reflection analytics not exceeded.

## Scaling

| Concern | Guidance |
|---------|----------|
| Bundle write amplification | Batch append reflections; avoid per-token writes |
| Compression cost | Offload to async worker tier; cap concurrent `compress_context` jobs per tenant |
| Prompt promotion | Single-writer per `PROMPT_VERSION_NAMESPACE`; use `expected_base_hash` |

## Security

- **Secrets:** supply credentials only through the host’s secret manager; never log full prompts if they contain customer data.
- **Integrity:** sign promoted prompt versions; reject `update_system_prompt` if review ticket is not in `approved` state.
- **Tenant isolation:** partition `bundle_id` and store keys by tenant id at the persistence layer.

## Observability

- Metrics: `curate_context_duration_ms`, `compression_ratio`, `quality_pass_rate`, `prompt_dry_run_count`, `prompt_promotion_count`.
- Tracing: propagate `session_id` and `bundle_id` on all tool spans.
