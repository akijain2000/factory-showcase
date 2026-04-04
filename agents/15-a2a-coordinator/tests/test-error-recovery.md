# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

`discover_agents` times out, `negotiate_protocol` returns `TRANSPORT_TIMEOUT`, and the message bus circuit opens for `delegate_task`. The coordinator must retry discovery, renegotiate, and avoid creating orphan handles under half-open bus state.

## Setup

- Agent config: `AGENT_DIRECTORY_URI=mock://directory`, `A2A_MESSAGE_BUS_REF=mock://bus`, retry policy: 2 attempts for read-only discovery, 1 renegotiation; breaker trips after three failed delegates.
- Tools mocked:
  - `discover_agents`: first → timeout; second → `{ "agents": [{ "id": "agentA", "skills": ["incident_triage"], "capability_version": "3.2" }] }`.
  - `negotiate_protocol`: first → `{ "error": "TRANSPORT_TIMEOUT", "retryable": true }`; second → `{ "protocol_id": "proto_77", "ok": true }`.
  - `delegate_task`: while bus circuit open → `{ "error": "CIRCUIT_OPEN", "retry_after_ms": 2000 }`; after half-open → `{ "task_handles": ["t1"], "ok": true }`.
  - `collect_results` / `resolve_conflicts`: idle success stubs if invoked.

## Steps

1. User sends: "Spin up triage on this trace—use agentA only."
2. Agent should: call `discover_agents`; retry on timeout until success or policy cap.
3. Agent should: call `negotiate_protocol` including `agentA`; retry once on transport timeout.
4. Agent should: on `CIRCUIT_OPEN` from `delegate_task`, backoff and retry rather than duplicating tasks with new ids blindly.
5. Agent should: only call `collect_results` after handles exist.

## Expected outcome

- Successful discovery and negotiation before any delegation attempt that expects delivery.
- At most one active `task_handle` for the same logical subtask after recovery (no unbounded fan-out retries).
- User-visible status mentions transient bus issues without leaking internal queue names with credentials.

## Pass criteria

- Fixture order: `discover_agents` success before final `negotiate_protocol` success before successful `delegate_task`.
- `delegate_task` retry count ≤ 2 in circuit-open script.
- Measurable: orphan handle count in mock bus store == 0 after test completion.
