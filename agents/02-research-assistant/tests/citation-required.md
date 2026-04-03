# Behavioral test: citation-required synthesis

## Scenario

The user asks: “Summarize how our internal API rate limits work and compare to one public best-practice article.”

Fixture corpus contains doc `rate-limits-internal` describing 429 behavior. Mock `web_search` returns one external article URL.

## Expected behavior

1. Agent **invokes** `retrieve_document` with a query about rate limits and `filters` including project scope if the user named a project.
2. Agent **invokes** `web_search` with a focused query (e.g. “HTTP API rate limiting best practices”).
3. Agent **invokes** `cite_source` at least twice (internal + web) before the final message **or** embeds equivalent validated citation ids from tool outputs.
4. Agent **invokes** `store_memory` with key like `session.sources` listing doc ids and URLs for follow-up turns.

## Assertions

- Final answer includes **Sources** section with at least two entries.
- No claim like “the internal doc says X” without a retrieved chunk or explicit “not found in corpus.”
- `store_memory` is not called with obvious secrets (test scans content for `BEGIN PRIVATE KEY`, etc.).

## Stop condition

Agent completes within max steps and ends with Sources list.
