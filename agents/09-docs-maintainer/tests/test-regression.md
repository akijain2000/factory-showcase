# Test: Regression — no drift, conflicting doc versions, references to deleted code

## Scenario

The maintainer must behave sensibly when there is nothing to sync, when two doc versions disagree, and when prose references symbols removed from code.

## Setup

- Agent config: `primary_branch: main`, `doc_branches: ["main","release/2.4"]`, `stale_link_policy: report`
- Tools mocked:
  - `diff_changes` (feature vs main) → `{ files: [] }` (no drift)
  - `read_source` on `docs/guides/api.md` (main) → mentions `fetch_legacy_user`
  - `read_source` on `docs/guides/api.md` (`release/2.4`) → mentions `fetch_user`
  - `search_codebase` for `fetch_legacy_user` → `{ hits: [] }`
  - `read_source` on `src/api/client.py` → contains `fetch_user` only; `fetch_legacy_user` removed
  - `check_links` → `{ broken: [{ url: "./legacy.html", reason: "404" }] }`

## Steps

1. User sends: "We merged everything—any doc updates needed from the last diff?"
2. Agent should: call `diff_changes`; on empty file list, report no code drift driving doc edits; avoid fabricated edits.
3. User sends: "Compare `docs/guides/api.md` on main vs release/2.4; they disagree on the client function name."
4. Agent should: call `read_source` for both branches (or explain tool limitation); present conflict; recommend single source of truth aligned with **main** code.
5. User sends: "main guide still documents fetch_legacy_user—fix it."
6. Agent should: call `search_codebase` / `read_source` on code; detect deleted symbol; call `update_doc` to align prose and examples with `fetch_user` only.
7. Agent should: call `check_links` on the guide; report `./legacy.html` 404 and fix or flag.

## Expected outcome

- No doc churn when diff is empty.
- Conflicting versions are explained, not silently merged.
- Stale symbol references removed or updated to match `src/api/client.py`; broken relative link addressed or explicitly listed.

## Pass criteria

- When `diff_changes` returns no files, zero `update_doc` calls **unless** user supplies separate evidence (here: user did in step 5—allowed).
- `update_doc` for step 6 includes rationale and matches current code symbol names from `read_source`.
- `check_links` results surfaced; no claim that `./legacy.html` works while mock says 404.
