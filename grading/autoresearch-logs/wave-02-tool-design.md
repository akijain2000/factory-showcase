# Wave 2: Tool Design — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 3 (Tool Design Quality)  
**Baseline:** Mean ~6.0/10 on this dimension (tools had schemas + return shapes but lacked production details)

## What was done

Enriched all 96 tool schema files across 20 agents with:
- Error taxonomy tables (domain-specific error codes with retryable flags)
- Timeouts and rate limits (per-tool defaults, exponential backoff with jitter)
- Idempotency keys for 56 mutating tools (with JSON schema alignment)
- Pagination for 12 list/query tools (cursor-based, page sizes)

## What INCREASES score (learnings)

1. **Error taxonomy with retryable flags** — The single most impactful addition. Without this, agents have no guidance on which errors to retry vs abort. Every tool needs at least TIMEOUT (retryable), INVALID_INPUT (not retryable), PERMISSION_DENIED (not retryable) + 2-3 domain-specific codes.
2. **Idempotency keys for mutating tools** — Production-critical. Without idempotency, retries on mutating tools can cause data corruption. Adding an optional `idempotency_key` field to the JSON schema gives agents safe retry semantics.
3. **Explicit timeouts** — Generic "use a timeout" is not enough. Each tool needs a specific default timeout based on its expected latency profile (file ops: 30s, API calls: 60s, batch jobs: 300s).
4. **Pagination for list tools** — Without pagination, agents that query large datasets will hit token limits. Cursor-based pagination with `next_cursor` in the response is the cleanest pattern.
5. **Domain-specific error codes** — Generic HTTP codes are not enough. `QUERY_TOO_EXPENSIVE`, `GRAPH_CYCLE_DETECTED`, `BUDGET_EXCEEDED` give the agent actionable information for plan adjustment.

## What DECREASES score (anti-patterns found)

1. **Missing error shapes entirely** — Tools without ANY error documentation force agents to guess error handling. This was the #1 gap in agents 11-20.
2. **Idempotency on read-only tools** — Adding idempotency to read-only tools is noise and signals misunderstanding of the concept. 40 read-only tools correctly excluded.
3. **Pagination on single-item tools** — Adding pagination to `move_file` or `create_directory` is wrong. Only 12/96 tools actually return lists.
4. **Rate limits without backoff strategy** — Saying "100 calls/min" without specifying backoff is incomplete. Always include: exponential with jitter, max retries, ceiling.
5. **Timeout without cancellation** — Long-running tools need both a timeout AND a way to cancel mid-execution. This is a gap we'll address in Wave 3 (source code).

## Metrics after Wave 2

- 96/96 tools: error taxonomy + timeouts
- 56/96 mutating tools: idempotency keys
- 12/96 list tools: pagination
- JSON schemas updated with optional idempotency_key fields
- Estimated dim 3 score: 8.5-9.0/10 (up from ~6.0)

## Remaining gap to 9/10

- Dry-run/preview mode for destructive tools (execute_ddl, move_file, etc.)
- Tool versioning (schema version field)
- Cross-tool dependency documentation (which tools must be called before others)
