# Tool: `execute_step`

## Purpose

Executes a single node in a directed acyclic graph (DAG) workflow: resolves inputs, runs the step’s handler, records status, and returns the step result plus identifiers of steps that are now eligible to run (dependencies satisfied).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "step_id": {
      "type": "string",
      "description": "Unique node id within the DAG instance.",
      "minLength": 1
    },
    "dag_id": {
      "type": "string",
      "description": "Workflow / DAG instance identifier.",
      "minLength": 1
    },
    "inputs": {
      "type": "object",
      "description": "Key-value inputs for this step (may include outputs from upstream steps).",
      "additionalProperties": true
    },
    "step_execution_id": { "type": "string", "maxLength": 128 }
  },
  "required": ["step_id", "dag_id", "inputs"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "step_id": "normalize_docs",
  "dag_id": "wf_7f3a",
  "status": "succeeded",
  "result": {
    "normalized_count": 12,
    "artifacts_uri": "s3://bucket/wf_7f3a/normalized/"
  },
  "next_steps": ["embed_chunks", "quality_check"],
  "execution": {
    "started_at": "2026-04-04T12:00:00.000Z",
    "finished_at": "2026-04-04T12:00:04.500Z"
  }
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| STEP_FAILED | no | Handler returned failure or validation error |
| DAG_NOT_FOUND | no | Unknown `dag_id` |
| DEPENDENCY_UNSATISFIED | no | Upstream steps not complete |
| HANDLER_TIMEOUT | yes | Step execution exceeded configured timeout |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 3600s (per-step `timeout_ms` may be lower)
- Rate limit: 200 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `step_execution_id` (optional field in arguments)
- Safe to retry: yes (handlers should be idempotent where `durability` is `required`)
- Duplicate detection window: 86400s

## Side effects

Mutates DAG run state (marks step complete, may enqueue downstream); may write artifacts per step configuration.
