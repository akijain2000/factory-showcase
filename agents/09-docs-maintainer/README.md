# Docs Maintainer Agent

**Pattern:** MCP-forward documentation sync  
**Goal:** Discover code changes, reconcile documentation, fix broken links, and search the codebase using **MCP**-hosted tools for consistent retrieval across editors and CI.

## Architecture

The agent is **MCP-forward**: the host discovers capabilities via **MCP** `tools/list` (or equivalent) and routes model **function calling** to those registered tools. **Multi-source retrieval** combines git diffs, file reads, and semantic search before any doc edit.

```
                    +------------------+
                    |   MCP Host       |
                    | (Cursor / CI)    |
                    +--------+---------+
                             |
              tools/list + resources
                             |
        +--------------------+--------------------+
        |                    |                    |
 +------v------+      +------v------+      +------v------+
 | read_source |      | diff_changes|      |search_codebase|
 +------+------+      +------+------+      +------+------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                      +------v------+
                      |  update_doc |
                      +------+------+
                             |
                      +------v------+
                      | check_links |
                      +-------------+
```

**Epistemic split:** `read_source` / `search_codebase` ground truth in the repo; `diff_changes` scopes edits; `update_doc` applies patches; `check_links` validates outbound integrity.

## Contents

| Path | Purpose |
|------|---------|
| `system-prompt.md` | MCP discovery + retrieval **rules** |
| `tools/` | MCP tool schemas (documented) |
| `tests/` | Sync behavior |
| `src/` | Client skeleton |

## Deployment

Register the same tool names on the MCP server so local and CI agents share behavior.
