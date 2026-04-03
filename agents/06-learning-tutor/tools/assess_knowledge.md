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

## Errors

- `LEARNER_NOT_FOUND` — create profile before assessment
- `TOPIC_UNKNOWN` — unknown topic code
