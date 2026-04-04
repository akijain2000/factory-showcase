# Tool: `discover_agents`

## Purpose

Query the **agent directory** for peers matching skills, trust tier, latency, and data residency constraints.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["required_skills"],
  "properties": {
    "required_skills": {
      "type": "array",
      "items": { "type": "string", "maxLength": 128 },
      "maxItems": 32
    },
    "trust_tier_max": {
      "type": "string",
      "enum": ["public", "partner", "internal", "regulated"],
      "default": "internal"
    },
    "max_latency_ms": { "type": "integer", "minimum": 10, "maximum": 600000 },
    "data_residency": {
      "type": "array",
      "items": { "type": "string", "maxLength": 16 },
      "maxItems": 8
    },
    "health_must_be": {
      "type": "string",
      "enum": ["ok", "degraded_acceptable", "any"],
      "default": "ok"
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "agents": [
    {
      "agent_id": "svc/code-analyzer@v3",
      "skills": ["static_analysis", "diff_review"],
      "capability_version": "3.2.1",
      "trust_tier": "internal",
      "p95_latency_ms": 4200,
      "health": "ok"
    }
  ],
  "truncated": false
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| DIRECTORY_UNAVAILABLE | yes | Agent directory backend unreachable or unhealthy |
| NO_MATCH | no | No agents satisfy the given skill, trust, or residency filters |
| DIRECTORY_TIMEOUT | yes | Directory query exceeded internal deadline |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 30s
- Rate limit: 120 calls per minute
- Backoff strategy: exponential with jitter

## Pagination

- Default page size: 50
- Cursor-based: returns `next_cursor` in response
- Max results per call: 200

## Side effects

Read-only against `AGENT_DIRECTORY_URI`. May update local cache with TTL. Does not contact peer agents directly.
