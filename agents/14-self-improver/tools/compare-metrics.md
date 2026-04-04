# Tool: `compare_metrics`

## Purpose

Compare evaluation metrics between a **baseline** run and a **candidate** run on the same `suite_version`, applying configured gates.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["baseline_run_id", "candidate_run_id", "suite_version"],
  "properties": {
    "baseline_run_id": { "type": "string", "maxLength": 128 },
    "candidate_run_id": { "type": "string", "maxLength": 128 },
    "suite_version": { "type": "string", "maxLength": 64 },
    "gate_profile": { "type": "string", "maxLength": 64, "default": "default" }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "deltas": {
    "primary_score_mean": 0.018,
    "failure_rate": -0.004,
    "latency_p95_ms": 120
  },
  "gates_pass": true,
  "notes": ["Candidate improves tool-call accuracy on JSON tasks; no regression on safety refusals."]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| INCOMPATIBLE_RUN_PAIR | no | Runs do not share `suite_version` |
| METRICS_UNAVAILABLE | yes | Metrics store unreachable |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Side effects

Read-only against `METRICS_STORE_URI` / artifact indexes; may write a **comparison report** record for audit. If runs mismatch `suite_version`, returns `INCOMPATIBLE_RUN_PAIR` without results.
