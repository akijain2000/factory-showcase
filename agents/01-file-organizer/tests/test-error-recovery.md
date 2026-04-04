# Test: Retryable error on list_files then success

## Scenario

`list_files` first returns a transient retryable error (e.g. `EAGAIN` / `TEMPORARY_UNAVAILABLE`); on the next call it succeeds. Validates one bounded retry before succeeding.

## Setup

- Agent config: `FILE_ORGANIZER_ROOT` set to fixture workspace; `FILE_ORGANIZER_MAX_STEPS` sufficient for retry + completion.
- Tools mocked: `list_files` (first call error payload with `retryable: true`, second call directory listing); `create_directory`, `move_file` succeed.

## Steps

1. User sends: "List everything under `inbox/` and tell me how many files there are."
2. Agent should: invoke `list_files` on `inbox`.
3. Tool returns: `{ "ok": false, "code": "TEMPORARY_UNAVAILABLE", "retryable": true, "message": "filesystem busy" }`
4. Agent should: wait/back off per policy, invoke `list_files` again with the same path (at most one automatic retry).
5. Tool returns: `{ "ok": true, "entries": ["a.txt", "b.txt"] }`
6. Agent should: answer with count 2 without spiraling into repeated failures.

## Expected outcome

- Exactly two `list_files` calls for the same path (retry once).
- Final user-visible message states two files and does not claim success before the second call.

## Pass criteria

- Retry count ≤ 1 for the same tool + args; trace ends in `ok` terminal state; no `move_file` or `create_directory` unless the user asked for moves.

---

# Test: Fatal error stops with summary

## Scenario

`move_file` returns a non-retryable error (e.g. destination exists and policy forbids overwrite). Agent must stop gracefully and summarize.

## Setup

- Agent config: `FILE_ORGANIZER_ROOT` at fixture root.
- Tools mocked: `list_files` ok; `create_directory` ok; `move_file` returns `{ "ok": false, "code": "DESTINATION_EXISTS", "retryable": false }`.

## Steps

1. User sends: "Move `inbox/note.txt` to `archive/note.txt`."
2. Agent should: plan, create `archive` if needed, invoke `move_file`.
3. Tool returns: fatal error as above.
4. Agent should: not blindly retry the same `move_file`; emit a short error summary and suggested next step (e.g. rename target or use different path).

## Expected outcome

- No more than one `move_file` for that pair without user confirmation.
- Final message includes error code or plain-language equivalent and does not claim the file was moved.

## Pass criteria

- Zero unbounded retry loop; assistant message length bounded; session terminates within `FILE_ORGANIZER_MAX_STEPS`.

---

# Test: Tool timeout handling

## Scenario

`list_files` hangs until the harness injects a timeout; agent surfaces timeout to the user and does not fabricate file listings.

## Setup

- Agent config: tool timeout budget per call (e.g. 5s) enforced by test double.
- Tools mocked: `list_files` first invocation raises or returns `{ "ok": false, "code": "TIMEOUT" }` after deadline.

## Steps

1. User sends: "What is under `projects/`?"
2. Agent should: call `list_files` on `projects/`.
3. Tool returns: timeout / `TIMEOUT` after simulated wait.
4. Agent should: report that the listing could not complete in time; offer retry or smaller scope; must not invent filenames.

## Expected outcome

- No fabricated file names in the final answer.
- User sees explicit timeout or "could not complete" wording.

## Pass criteria

- Assertions pass that final message contains no paths not returned by a successful tool call in the trace.

---

# Test: Circuit breaker after consecutive failures

## Scenario

`create_directory` fails repeatedly with retryable errors; after N failures (e.g. 3), circuit opens and agent stops calling the tool and summarizes.

## Setup

- Agent config: circuit breaker threshold = 3 consecutive failures on same tool+path pattern.
- Tools mocked: `create_directory` always returns `{ "ok": false, "code": "STORAGE_QUOTA", "retryable": true }`.

## Steps

1. User sends: "Create `by-type/pdf` under the workspace root."
2. Agent should: invoke `create_directory` for `by-type/pdf`.
3. Tool returns: retryable failure (repeat for each attempt).
4. Agent should: stop after breaker trips (≤ 3 attempts or policy max); explain circuit breaker / repeated failure; do not call `move_file` into missing dirs as if they exist.

## Expected outcome

- `create_directory` call count ≤ configured breaker limit.
- Final message explains blocked progress without false success.

## Pass criteria

- Measurable cap on tool invocations; no downstream mutating tools assuming directory creation succeeded.
