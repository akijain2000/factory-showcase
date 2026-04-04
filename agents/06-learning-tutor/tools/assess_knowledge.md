# Tool: `assess_knowledge`

## Purpose

Probe learner mastery for a topic or skill subtree and return structured gaps and confidence.

## Invocation

- **Type:** function / MCP tool  
- **Name:** `assess_knowledge`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learner_id` | string | yes | Stable learner identifier |
| `topic` | string | yes | Topic or standard code (e.g., `algebra.quadratics`) |
| `depth` | string | no | `quick` \| `standard` \| `deep` (default `standard`) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `estimated_level` | number | 0.0–1.0 coarse mastery |
| `gaps` | array of string | Misconceptions or missing prerequisites |
| `strengths` | array of string | Reliable sub-skills |
| `recommended_focus` | string | One-sentence next focus |

## Error taxonomy

| Code | Retryable | Description |
|------|-----------|-------------|
| LEARNER_NOT_FOUND | no | Create profile before assessment |
| TOPIC_UNKNOWN | no | Unknown topic code |
| ASSESSMENT_TIMEOUT | yes | Model or datastore slow |
| TIMEOUT | yes | Operation exceeded time limit |
| INVALID_INPUT | no | Malformed arguments |
| PERMISSION_DENIED | no | Insufficient access |

## Timeouts and rate limits

- Default timeout: 45s
- Rate limit: 60 calls per minute
- Backoff strategy: exponential with jitter

## Errors

- `LEARNER_NOT_FOUND` — create profile before assessment
- `TOPIC_UNKNOWN` — unknown topic code
