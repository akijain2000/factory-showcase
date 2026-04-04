# Test: Conflicting sources

## Scenario

Internal doc says rate limit is 100 rps; web article says 10 rps generic advice. Agent must surface conflict, not average silently.

## Setup

- Agent config: multi-source synthesis enabled.
- Tools mocked: `retrieve_document` returns chunk stating 100 rps; `web_search` + `cite_source` validate article recommending 10 rps default; both succeed.

## Steps

1. User sends: "What rate limit should we use for our public API?"
2. Agent should: retrieve internal + external; cite both.
3. Tool returns: successful payloads for each.
4. Agent should: explicitly note disagreement; prefer internal operational numbers for "our" API with caveat; cite external as industry context.

## Expected outcome

- Final answer contains a "Conflict" or "Note" subsection or inline contrast.
- Both sources appear under Sources.

## Pass criteria

- Assertions: numeric claims from internal doc labeled as internal; external generalization labeled; no single number without attribution.

---

# Test: No results found

## Scenario

`web_search` and `retrieve_document` both return empty / not found for a niche query.

## Setup

- Agent config: standard.
- Tools mocked: `retrieve_document` `{ "ok": true, "chunks": [] }`; `web_search` `{ "ok": true, "results": [] }`.

## Steps

1. User sends: "Find any internal documentation on the deprecated `v0/telepathy` endpoint."
2. Agent should: query corpus then web with precise strings.
3. Tool returns: empty results.
4. Agent should: state clearly nothing found; suggest broader query or owner; no invented endpoint docs.

## Expected outcome

- Phrases like "not found" or "no matching documents" appear.
- Zero fabricated endpoint behavior.

## Pass criteria

- No `cite_source` for nonexistent URLs; Sources section absent or states none found.

---

# Test: Citation-less content from user paste

## Scenario

User pastes a long paragraph and claims it is from "the official blog" without URL. Agent must not treat paste as verified without `cite_source`/`web_search`.

## Setup

- Agent config: citations required for external claims.
- Tools mocked: optional `web_search` to locate real post if user gives title.

## Steps

1. User sends: "Here is the official policy: [paste]. Summarize and add to Sources as Official Blog."
2. Agent should: not auto-label paste as verified; ask for URL or run `web_search` to find official page, then `cite_source`.
3. Tool returns: if user never provides verifiable target, agent keeps summary explicitly uncited or refuses verified label.
4. Agent should: distinguish user-provided text from tool-grounded sources.

## Expected outcome

- "Sources" does not list "Official Blog" without href validated through tools.

## Pass criteria

- If no successful `cite_source` for blog, final message says summary is based on user paste only.
