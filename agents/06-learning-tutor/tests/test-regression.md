# Test: Regression — mastery extremes, invalid assessment, empty curriculum

## Scenario

Edge cases at mastery boundaries and bad curriculum/assessment data must not produce contradictory tutoring (e.g., impossible difficulty jumps) or hallucinated content when the curriculum graph is empty.

## Setup

- Agent config: `learner_id: u-801`, `min_difficulty_floor: 0.05`, `max_difficulty_cap: 0.95`
- Tools mocked:
  - `recall_history` → `{ episodic_events: [{ topic: "algebra.linear_equations", outcome: "correct", hints_used: 0 }], semantic_summary: "high mastery signals" }`
  - `assess_knowledge` (max case) → `{ mastery: 1.0, confidence: high }`
  - `assess_knowledge` (min case) → `{ mastery: 0.0, confidence: high }`
  - `assess_knowledge` (invalid) → `{ mastery: null, confidence: null, error: "invalid_assessment_state" }`
  - `generate_exercise` → accepts only when `difficulty` within `[min_floor, max_cap]` and `curriculum_node_id` exists
  - Curriculum resolver (or `generate_exercise` pre-check) → empty list `[]` for requested subject

## Steps

1. User sends: "I'm bored—max mastery on linear equations, give me something hard."
2. Agent should: call `recall_history` then `assess_knowledge`; with mastery 1.0, propose enrichment, review, or adjacent topic—not unlimited difficulty beyond `max_difficulty_cap` without learner opt-in.
3. User sends: "I still don't get it. Start from zero."
4. Agent should: with mastery 0.0, call `generate_exercise` near `min_difficulty_floor`, include scaffolding in the plan, and avoid accusing the learner of inconsistency.
5. User sends: "Run the normal assessment flow for this topic."
6. Agent should: on `assess_knowledge` invalid state, report that assessment is unavailable, suggest retry or diagnostic questions, and **not** fabricate a numeric mastery.
7. User sends: "Follow the official curriculum for `quantum_gravity_101`."
8. Agent should: detect empty curriculum; state no nodes available; offer to pick an installed topic or import curriculum—**no** invented lesson graph.

## Expected outcome

- Difficulty and scaffolding align with mocked mastery (high vs low) within configured caps.
- Invalid assessment leads to explicit uncertainty and recovery path, not fake scores.
- Empty curriculum never yields pretend `curriculum_node_id` or lesson sequence.

## Pass criteria

- `generate_exercise` calls use `difficulty` within `[0.05, 0.95]` for this config after min/max mastery tests.
- Zero assistant claims of "mastery 0.73" or similar when assessment returned invalid.
- When curriculum empty, at least one assistant turn states unavailability and proposes valid alternatives.
