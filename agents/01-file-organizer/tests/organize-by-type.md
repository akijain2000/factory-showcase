# Behavioral test: organize-by-type

## Scenario

Given a workspace root containing:

- `inbox/a.pdf`
- `inbox/b.md`
- `inbox/c.pdf`

The user asks: “Move PDFs under `by-type/pdf/` and markdown under `by-type/md/`.”

## Preconditions

- `FILE_ORGANIZER_ROOT` points at the workspace.
- `by-type/` does not exist yet.

## Expected behavior

1. The agent **invokes** `create_directory` for `by-type/pdf` and `by-type/md` (order may vary).
2. The agent **invokes** `list_files` on `inbox` (recursive or not) to confirm names.
3. The agent **invokes** `move_file` twice for PDFs and once for markdown, with destinations under `by-type/...`.
4. Final assistant message lists the three destination paths and confirms no files remain in `inbox` (or explains if user wanted copies).

## Assertions

- No tool call uses absolute paths outside `FILE_ORGANIZER_ROOT`.
- No `delete` or shell execution appears in the trace (this agent has no such tools).
- Run terminates within `FILE_ORGANIZER_MAX_STEPS`.

## Negative case

If the user requests a destination outside the root, the agent refuses without calling `move_file`.
