# Tool: `check_health`

## Purpose

Probe service health endpoints, dependency graphs, or SLO panels.

## Invocation

**Function calling** name: `check_health`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `service` | string | yes | Logical service name |
| `region` | string | no | Region or `global` |
| `probe_types` | array | no | e.g. `["http", "queue_depth", "db_ping"]` |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `healthy` \| `degraded` \| `down` \| `unknown` |
| `checks` | array | Per-probe results with latency/error |
| `as_of` | string | ISO-8601 |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| SERVICE_UNKNOWN | no | `service` not in catalog |
| PROBE_TIMEOUT | yes | One or more probes timed out |
| OBSERVABILITY_UNAVAILABLE | yes | Metrics or health API unreachable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `SERVICE_UNKNOWN`
- `PROBE_TIMEOUT`
