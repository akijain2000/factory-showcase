# Tool: `resume_from_checkpoint`

## Purpose

Resumes DAG execution from a persisted checkpoint after interruption, failure, or deliberate pause. Restores run state (completed steps, partial outputs) and returns pending steps still to execute.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "checkpoint_id": {
      "type": "string",
      "description": "Identifier of the snapshot to restore.",
      "minLength": 1
    },
    "dag_id": {
      "type": "string",
      "description": "Workflow / DAG instance to resume.",
      "minLength": 1
    },
    "resume_token": { "type": "string", "maxLength": 128 }
  },
  "required": ["checkpoint_id", "dag_id"],
  "additionalProperties": false
}
```

## Return shape

```json
{
  "checkpoint_id": "ckpt_9qm2",
  "dag_id": "wf_7f3a",
  "restored_state": {
    "run_status": "running",
    "completed_steps": ["ingest", "normalize_docs"],
    "failed_steps": [],
    "variables": {
      "normalized_count": 12
    },
    "restored_at": "2026-04-04T12:05:00.000Z"
  },
  "pending_steps": ["embed_chunks", "quality_check", "index_build"]
}
```

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| CHECKPOINT_NOT_FOUND | no | Unknown `checkpoint_id` |
| DAG_NOT_FOUND | no | Unknown `dag_id` or run not resumable |
| RUN_CONFLICT | no | Another worker holds lease or state advanced |
| STORE_UNAVAILABLE | yes | Checkpoint store error |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 60s
- Rate limit: 40 calls per minute
- Backoff strategy: exponential with jitter

## Idempotency

- Idempotency key: `resume_token` (optional field in arguments)
- Safe to retry: yes
- Duplicate detection window: 3600s

## Side effects

Mutates active run state (loads checkpoint into orchestrator memory / store); may transition run from `paused` or `failed` to `running`.
