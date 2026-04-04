# Test: Regression — discovery timeout, protocol version mismatch, circular delegation

## Scenario

Peer discovery stalls past SLO, two capable agents advertise incompatible `capability_version` for the same schema, and task decomposition would create a delegation cycle (A→B→A). The coordinator must time out cleanly, narrow peers, and refuse cyclic graphs.

## Setup

- Agent config: `AGENT_DIRECTORY_URI=mock://directory`, discovery `deadline_ms=800`, protocol requires matching `payload_schema_ref` and `capability_version >= 3.0`.
- Tools mocked:
  - `discover_agents`: slow path → first call times out at 900ms; second call (if agent retries with smaller scope) → `{ "agents": [{ "id": "agentA", "capability_version": "3.2" }, { "id": "agentB", "capability_version": "2.0" }] }`.
  - `negotiate_protocol`: with both A and B → `{ "error": "SCHEMA_MISMATCH", "peer": "agentB" }`; with A only → `{ "protocol_id": "proto_a", "ok": true }`.
  - `delegate_task`: if planner supplies edges `[A→B, B→A]` on same root task → `{ "error": "CIRCULAR_DELEGATION", "cycle": ["A", "B", "A"] }`.
  - `collect_results` / `resolve_conflicts`: stubs.

## Steps

1. User sends: "Use everyone available for parallel diagnosis—fast."
2. Agent should: call `discover_agents` within deadline handling; surface timeout if directory violates SLO unless narrowed query succeeds.
3. Agent should: attempt `negotiate_protocol`; on mismatch, drop `agentB` and renegotiate with v3.x peers only.
4. Agent should: when building delegation DAG, detect cycles before dispatch; revise plan to acyclic tree or single owner.
5. Agent should: only call `delegate_task` after successful `protocol_id`.

## Expected outcome

- Final successful `negotiate_protocol` includes no v2 peer when schema requires v3.
- No `delegate_task` issued under failed protocol attempt.
- Cyclic plan rewritten or rejected with explicit `CIRCULAR_DELEGATION` handling—no infinite ping-pong.

## Pass criteria

- Fixture asserts second negotiation excludes `agentB` from participant list.
- At least one `SCHEMA_MISMATCH` or explicit mismatch handling before success path.
- Measurable: graph validator on planned delegations reports acyclicity score == pass before any dispatch.
