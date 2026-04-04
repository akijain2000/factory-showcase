# Test: Regression — context window overflow, stale context, conflicting sources

## Scenario

The working set exceeds `CONTEXT_MAX_TOKENS` after merge, two sources disagree on the same incident ID, and a previously curated window is stale relative to a newer upstream log tail. The agent must compress, reconcile, and avoid serving contradictory facts as ground truth.

## Setup

- Agent config: `CONTEXT_MAX_TOKENS=32000`, `CONTEXT_STORE_URI=mock://context-store`, freshness policy: items older than `T-45m` flagged `stale unless corroborated`.
- Tools mocked:
  - `curate_context`: returns `bundle_id: bnd_conflict`, items including (A) ticketing API summary `status: resolved`, (B) live log tail `status: investigating` for same `incident_id`.
  - `evaluate_context_quality`: first call → `{ "pass": false, "gaps": ["source_conflict", "token_pressure"] }`; after re-curation → `{ "pass": true, "gaps": [] }`.
  - `compress_context`: reduces `est_tokens` from `34000` to `24000` while preserving both conflicting items with explicit `provenance` metadata (implementation-defined shape).
  - `reflect_on_output`: optional if agent narrates reconciliation strategy.

## Steps

1. User sends: "Give me a single timeline for incident INC-4412 using everything attached."
2. Agent should: run `curate_context` and detect token pressure or conflicts via `evaluate_context_quality`.
3. Agent should: prefer fresher authoritative source per policy (e.g. log tail over stale ticket) or present both with explicit conflict labeling—not a flat merged lie.
4. Agent should: invoke `compress_context` when over `CONTEXT_MAX_TOKENS` or when quality gate cites `token_pressure`.
5. Agent should: re-run `evaluate_context_quality` until `pass: true` or stop with explicit human-needed conflict if policy forbids auto-resolution.

## Expected outcome

- Final user-visible narrative states the conflict or the chosen resolution rule (e.g. "prefer stream source after T0") in plain language.
- No single asserted final status unless supported by the chosen source or both agree after reconciliation.
- Post-compression `est_tokens` ≤ `CONTEXT_MAX_TOKENS` in mocked tool responses.

## Pass criteria

- `compress_context` called when pre-compression estimate exceeds limit (fixture checks `est_tokens` before/after).
- At least two `evaluate_context_quality` calls with transition from `pass: false` (conflict/pressure) to `pass: true` OR explicit escalation object if conflict unresolved by policy.
- Measurable: diff of final answer against forbidden phrases (`"definitely resolved"`) when logs still say investigating—must not appear unless reconciliation documented.
