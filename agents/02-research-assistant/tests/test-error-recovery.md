# Test: Retryable error on web_search then success

## Scenario

First `web_search` call hits rate limit (retryable); second succeeds. Agent retries once then continues synthesis.

## Setup

- Agent config: project corpus enabled; max steps allows retry + cite flow.
- Tools mocked: `web_search` (first `{ "ok": false, "code": "RATE_LIMIT", "retryable": true }`, second `{ "ok": true, "results": [{ "url": "https://example.com/ratelimits", "title": "..." }] }`); `retrieve_document`, `cite_source`, `store_memory` succeed.

## Steps

1. User sends: "Find one public article on API rate limiting best practices and cite it."
2. Agent should: invoke `web_search` with focused query.
3. Tool returns: retryable rate limit.
4. Agent should: single backoff retry of `web_search` with same or tightened query.
5. Tool returns: successful results.
6. Agent should: invoke `cite_source` for chosen URL, then answer with Sources.

## Expected outcome

- At most two `web_search` calls for the same intent before success or giving up.
- Final answer includes cited external source.

## Pass criteria

- Retry count ≤ 1 for identical search args; trace includes successful `cite_source` or equivalent validated citation ids.

---

# Test: Fatal error from retrieve_document

## Scenario

Internal corpus returns permanent failure (doc revoked / index corrupt). Agent stops forward progress on that retrieval path and summarizes.

## Setup

- Agent config: internal doc id user references does not exist in index.
- Tools mocked: `retrieve_document` returns `{ "ok": false, "code": "DOCUMENT_NOT_FOUND", "retryable": false }`.

## Steps

1. User sends: "What does internal doc `rate-limits-internal` say about 429 responses?"
2. Agent should: invoke `retrieve_document` with query + filters.
3. Tool returns: fatal not-found.
4. Agent should: not assume content; state doc unavailable; avoid inventing 429 behavior.

## Expected outcome

- No fabricated internal API details.
- User sees explicit "not found" or equivalent.

## Pass criteria

- Zero claims attributed to `rate-limits-internal` without a successful retrieval chunk in trace.

---

# Test: cite_source timeout

## Scenario

`cite_source` times out while validating a URL; agent reports validation could not complete and does not mark claim as fully cited.

## Setup

- Agent config: per-tool timeout enforced by harness.
- Tools mocked: `web_search` ok; `cite_source` returns `{ "ok": false, "code": "TIMEOUT" }`.

## Steps

1. User sends: "Search for OAuth2 PKCE overview and give me one cited bullet."
2. Agent should: `web_search`, then `cite_source` for selected result.
3. Tool returns: timeout.
4. Agent should: say citation validation incomplete; offer retry; distinguish uncited summary vs cited.

## Expected outcome

- Final message does not label the bullet as fully verified/cited if `cite_source` never succeeded.

## Pass criteria

- Assertions: no "Sources" entry claiming validation without successful `cite_source` output.

---

# Test: Circuit breaker on consecutive retrieve failures

## Scenario

`retrieve_document` fails three times with retryable `INDEX_TEMPORARY_ERROR`; breaker opens; agent stops hammering index.

## Setup

- Agent config: breaker after 3 consecutive failures on `retrieve_document`.
- Tools mocked: always `{ "ok": false, "code": "INDEX_TEMPORARY_ERROR", "retryable": true }`.

## Steps

1. User sends: "Pull everything about billing from internal docs."
2. Agent should: call `retrieve_document` with billing query.
3. Tool returns: repeated retryable failures.
4. Agent should: cap retries at breaker; summarize index unavailable; suggest later retry or human.

## Expected outcome

- `retrieve_document` invocations ≤ breaker limit (e.g. 3) without user-approved escalation.

## Pass criteria

- Bounded tool calls; no hallucinated billing policy text.
