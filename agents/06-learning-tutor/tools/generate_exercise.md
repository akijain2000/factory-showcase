# Tool: `generate_exercise`

## Purpose

Create a single practice item aligned to learner level and known gaps.

## Invocation

**Function calling** name: `generate_exercise`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `learner_id` | string | yes | Learner id |
| `topic` | string | yes | Topic code |
| `difficulty` | number | yes | 0.0–1.0 target difficulty |
| `format` | string | no | `mcq` \| `short_answer` \| `worked_steps` |
| `avoid_patterns` | array | no | Patterns to avoid (from episodic memory) |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `exercise_id` | string | Unique id for later `store_progress` |
| `prompt` | string | Learner-facing question |
| `rubric` | object | Optional grading hints (not shown to learner) |
| `expected_time_minutes` | number | Estimated effort |

## Errors

- `DIFFICULTY_OUT_OF_RANGE`
- `TOPIC_LOCKED` — prerequisite not met
