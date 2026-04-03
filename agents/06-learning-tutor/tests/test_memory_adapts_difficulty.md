# Behavioral test: Memory adapts difficulty

## Scenario

1. Learner `u-100` has **episodic** history showing three consecutive **incorrect** outcomes on `calculus.derivatives` with high `hints_used`.
2. Tutor starts a new session and **invokes** `recall_history` with `mode: both` for that topic.
3. Tutor then **invokes** `assess_knowledge` for the same topic.
4. Tutor **invokes** `generate_exercise` with a **lower** `difficulty` than the previous session’s average (e.g., 0.35 vs 0.65).

## Expected behavior

- The agent **must** call `recall_history` before `generate_exercise` when history exists (per system **rules**).
- `generate_exercise` input **must** include `avoid_patterns` or difficulty reduction consistent with episodic failure pattern (no harder drill without justification).
- After the learner submits an answer, the agent **invokes** `store_progress` with accurate `outcome` and optional `notes` capturing misconception if stated.
- The agent **does not** claim prior sessions occurred if `episodic_events` is empty.

## Failure modes

- Skipping `store_progress` after a completed attempt → **fail**
- Increasing difficulty despite three failures without explicit learner request → **fail**
