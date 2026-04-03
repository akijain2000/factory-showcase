# Deploy: Security-Hardened Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `SECURITY_AGENT_POLICY_BUNDLE_REF` | yes | Signed policy location (rotation supported) |
| `SECURITY_AGENT_AUDIT_SINK_REF` | yes | Append-only audit destination |
| `MODEL_API_ENDPOINT` | yes | Inner model router |
| `SECURITY_AGENT_INJECTION_MODE` | optional | `fast_rules`, `hybrid`, or `full` default |

## Health check

- `GET /healthz`: process up.
- `GET /readyz`: policy bundle signature valid; audit sink append probe succeeds; schema registry for `validate_output` reachable.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| Input size | Match `sanitize_input` max; reject early at edge |
| Audit throughput | Batch or async shipper to avoid blocking user path |
| Permission checks | Cache decisions 30–120s where safe (include scope in cache key) |

## Operational notes

- **Key material** for policy signing lives in KMS/HSM; never in environment variables.
- **Red team** regularly updates injection detectors; treat model-assisted signals as probabilistic.
- **Break-glass** roles must expire automatically and emit `severity: critical` audit events.
