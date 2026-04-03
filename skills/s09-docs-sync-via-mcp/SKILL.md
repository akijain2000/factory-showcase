---
name: s09-docs-sync-via-mcp
description: Finds MCP tools and syncs documentation with code, tickets, or external wikis. Use when docs lag behind implementation or the docs-maintainer agent pulls multi-source truth.
---

# Documentation sync via MCP

## Goal / overview

Keep user-facing and operator docs aligned with authoritative sources by pulling structured facts through MCP tools and merging them into the doc set. Pairs with agent `09-docs-maintainer`.

## When to use

- README claims features that code no longer exposes.
- Runbooks omit new flags or environment variables.
- Multiple systems (wiki, repo, ticket) disagree on the same procedure.

## Steps

1. Enumerate available MCP servers and tools from descriptors; note required auth steps before calling write-capable tools.
2. Define the **source of truth order** for this task (e.g. code constants > OpenAPI > ticket acceptance criteria > wiki).
3. Fetch current text from each source: repo files via read tools, external pages via approved connectors, tickets via search tools when available.
4. **Freshness scoring**: Check document age and last-updated metadata; compare against source timestamps (e.g. git commits, ticket updated time, MCP response metadata). Flag sections where the authoritative source is newer than the doc text or where age exceeds a task-specific staleness threshold.
5. Diff semantic content: commands, flags, endpoints, limits, SLAs—not just punctuation.
6. Patch docs with minimal edits; preserve tone and section structure unless a section is obsolete.
7. Run link and anchor checks when tooling exists; record remaining manual verifications.

## Output format

- **Source map**: topic → authoritative location → last observed revision or timestamp.
- **Change list**: file, section, old summary, new summary, reason.
- **Residual risks**: unverified claims or blocked MCP calls.

## Gotchas

- Write tools can overwrite human edits; prefer patches with reviewable diffs.
- Cached MCP responses may be stale; include fetch metadata in notes.
- Secrets must never be copied into docs; reference secret manager names only.

## Test scenarios

1. **Flag rename**: Code renames `FEATURE_X` to `FEATURE_Y`; sync should update env tables across README and ops doc with one consistent name.
2. **MCP auth missing**: Server requires `mcp_auth`; workflow should stop, list the gap, and avoid partial writes.
3. **Wiki vs code clash**: Wiki documents an endpoint the OpenAPI file removed; doc update should follow OpenAPI and annotate the wiki as outdated.
