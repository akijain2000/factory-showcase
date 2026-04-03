# Research Assistant Agent

A **ReAct + RAG** agent that searches multiple sources, retrieves documents, maintains **session memory**, and answers with **explicit citations**.

## Audience

Analysts, engineers, and PMs who need traceable research: every non-trivial claim should tie to a retrieved or web-fetched source.

## Quickstart

1. Load `system-prompt.md` as the system message.
2. Register tools from `tools/` (web search, retrieval, memory, citation helper).
3. Configure vector store / document index URLs via environment variables.
4. Validate scenarios in `tests/` in CI with mocked search and retrieval.

## Configuration

| Variable | Description |
|----------|-------------|
| `RESEARCH_MEMORY_STORE` | URI for durable memory backend (or `memory://` for dev) |
| `RESEARCH_DOC_INDEX` | Retrieval endpoint or collection id |
| `RESEARCH_MAX_WEB_RESULTS` | Cap on web hits per query |

## Architecture

```
 +-------------+     +-------------------+     +------------------+
 | User / API  |---->| ReAct orchestrator |---->| Model (plan/act)  |
 +-------------+     +---------+---------+     +---------+--------+
                               |                           |
           +-------------------+---------------------------+
           |                   |                           |
           v                   v                           v
   +---------------+   +---------------+           +---------------+
   |  web_search   |   |retrieve_document|         | store_memory  |
   +-------+-------+   +-------+-------+         +-------+-------+
           |                   |                           |
           v                   v                           v
   +---------------+   +---------------+           +---------------+
   | Search provider|   | Vector / DB   |           | Memory store  |
   +---------------+   +---------------+           +---------------+
                               |
                               v
                       +---------------+
                       |  cite_source  |  (format + validate cites)
                       +---------------+
```

## Memory model

- **Working context:** recent turns + tool outputs in the message window.
- **Durable memory:** user/session-scoped notes via `store_memory` (see tool contract for keys and TTL).

## Testing

Behavioral specs live under `tests/`; automate with fixture documents and mocked HTTP.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
