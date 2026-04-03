# Test: schema mismatch blocks delegation; evidence-first resolution

## Scenario

Two specialist agents can tackle a diagnosis task, but one advertises an older **capability_version** with an incompatible error schema. After fixing negotiation participants, parallel delegates return **conflicting** root-cause labels.

## Given

- `discover_agents` returns `agentA` (v3.2) and `agentB` (v2.0) both matching `required_skills: ["incident_triage"]`.
- `payload_schema_ref` is `schemas/triage_input_v3.json`.
- `error_schema_ref` requires fields `{ "code", "retryable", "detail_ref" }`; v2.0 peer cannot comply.
- After restricting peers to v3.x only, two successful results disagree: `memory_pressure` vs. `query_plan_regression`.

## When

1. The coordinator calls `discover_agents` and attempts `negotiate_protocol` including both A and B.
2. Negotiation fails with `SCHEMA_MISMATCH` (or equivalent) tied to `agentB`.
3. The coordinator re-runs `negotiate_protocol` with `peer_agent_ids` containing only v3-capable agents.
4. The coordinator calls `delegate_task` with two parallel subtasks and collects via `collect_results` with `wait_policy: all_terminal`.
5. `collect_results` sets `conflicts: true` and returns `conflict_set_id`.
6. The coordinator calls `resolve_conflicts` with `strategy: evidence_first`.

## Then

- No `delegate_task` occurs under a failed `protocol_id`; handles are not created for the mismatched negotiation attempt.
- Post-fix delegation produces two `task_handles` in **queued or active** states before collection completes.
- `resolve_conflicts` selects the output with **stronger evidence references** (stack trace / metric series) per tool policy, or opens `human_escalation` if neither meets evidence threshold—test fixture must assert the expected branch explicitly.
- Final answer includes a **provenance map** from agent id to contribution without leaking raw vault tokens.
