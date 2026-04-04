# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

Doc maintenance workflows depend on codebase search, diffs, and link checkers. Transient failures should be retried; persistent failures should halt edits and leave a clear audit trail rather than silent doc corruption.

## Setup

- Agent config: `max_tool_retries: 2`, `read_timeout_ms: 6000`, `circuit_breaker: { on_tool: "update_doc", failures_before_open: 2, cooldown_s: 120 }`
- Tools mocked:
  - `diff_changes` → attempt 1: timeout; attempt 2: `{ files: [{ path: "src/api/client.py", change: "rename fetchUser→fetch_user" }] }`
  - `search_codebase` → success `{ hits: [{ path: "docs/guides/api.md", line: 102 }] }`
  - `read_source` → success for code and markdown slices
  - `update_doc` → first call `500`; second call `500`; circuit opens (third call rejected with `circuit_open`)
  - `check_links` → `{ status: "ok", broken: [] }`

## Steps

1. User sends: "Sync docs with the feature branch diff; fix the renamed function in api guide."
2. Agent should: call `diff_changes`; retry once on timeout; proceed with file list.
3. Agent should: call `search_codebase` and `read_source` before any edit proposal.
4. Agent should: call `update_doc` with grounded patch; on 500, retry once; on second failure and circuit open, stop mutating; output proposed patch as text for human application.
5. Agent should: optionally call `check_links` on the markdown path if a patch was applied in a partial success scenario; if no write succeeded, still report link status only on last known good revision or skip with reason.

## Expected outcome

- No more than two `update_doc` attempts before circuit open in this mock.
- User receives either confirmed write success **or** explicit failure with copyable patch—never “done” without tool confirmation.
- No invented rename: `fetch_user` must match `read_source` on `src/api/client.py`.

## Pass criteria

- `read_source` (code + doc) invoked before first `update_doc` attempt.
- `update_doc` calls ≤ 2 when both return 500; zero calls while circuit open.
- Final message states write failure and next human step when circuit trips.
