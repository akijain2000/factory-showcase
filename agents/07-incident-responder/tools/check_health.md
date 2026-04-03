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

## Errors

- `SERVICE_UNKNOWN`
- `PROBE_TIMEOUT`
