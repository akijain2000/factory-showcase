# Behavioral test: Doc sync follows diff evidence

## Scenario

1. `diff_changes` between `main` and feature branch shows a renamed public function in `src/api/client.py` and no doc updates yet.
2. Agent **invokes** `search_codebase` for the old symbol and finds references in `docs/guides/api.md`.
3. Agent **invokes** `read_source` on both the code file (new signature) and the markdown file (stale section).
4. Agent **invokes** `update_doc` with a patch that renames the function in prose and updates the example snippet to match **tool**-read source.
5. Agent **invokes** `check_links` on `docs/guides/api.md`.

## Expected behavior

- `update_doc` **must** include a non-empty `rationale` string.
- Agent **does not** invent new API parameters absent from `read_source`.
- If `check_links` returns `broken` entries, agent reports them and either fixes relative links or stops with explicit next step—**never** silently ignores.
- Agent uses **MCP** **tool** discovery assumptions: if a tool is missing, it states that and falls back to read-only guidance.

## Failure modes

- Editing docs without prior `read_source` or `diff_changes` grounding → **fail**
- Claiming links pass when `check_links` reported `broken` → **fail**
