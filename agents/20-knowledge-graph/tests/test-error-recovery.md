# Test: extraction failures, traversal timeouts, and partial graph recovery

## Scenario

Entity extraction intermittently fails on a noisy document, `traverse_graph` times out on a broad hop limit, and `query_subgraph` returns partial pages. The agent retries bounded times, narrows traversal parameters, and still produces a grounded answer with coverage caveats.

## Setup

- Agent config: `GRAPH_STORE_REF=graph://harness`, `GRAPH_EMBED_INDEX_REF=idx://harness`, max traversal hops default `6`, per-call deadline `3000ms`.
- Tools mocked:
  - `extract_entities` → first `{ "ok": false, "error": "NLP_TRANSIENT" }`, second `{ "ok": true, "entities": [{ "id": "e1", "type": "Org", "name": "Acme" }] }`
  - `map_relationships` → `{ "ok": true, "edges": [{ "id": "edge_1", "s": "e1", "p": "OWNS", "o": "e2" }] }`
  - `traverse_graph` → first `{ "ok": false, "error": "TIMEOUT" }`; second with `max_hops: 2` returns `{ "ok": true, "paths": [...] }`
  - `query_subgraph` → `{ "ok": true, "nodes": [...], "truncated": true, "next_cursor": "cur_1" }`
  - `reason_over_path` → `{ "ok": true, "answer": "...", "support_paths": ["edge_1"] }`

## Steps

1. User sends: "Ingest memo_doc_22 and tell me what Acme owns."
2. Agent should: call `extract_entities`, retry once on `NLP_TRANSIENT`, then `map_relationships`.
3. Agent should: call `traverse_graph` from seed `e1`; on `TIMEOUT`, reduce `max_hops` or predicates and retry once.
4. Agent should: call `query_subgraph` for neighborhood context; if `truncated`, optionally follow `next_cursor` within harness limits or state truncation in the answer.
5. Agent should: call `reason_over_path` only with edges from successful traversals/subgraph.
6. Agent should: tell the user if results were truncated or recovered after retry.

## Expected outcome

- Final answer references only entities and edges returned by successful tool calls.
- User-visible text mentions timeout recovery or truncated subgraph when mocks indicate so.
- No invented organizations beyond `Acme` fixture unless explicitly marked hypothetical (should not happen).

## Pass criteria

- At most two `extract_entities` calls; at most two `traverse_graph` calls.
- `reason_over_path.support_paths` ⊆ ids returned by `map_relationships` / `traverse_graph` in harness validation.
- Answer includes caveat when `truncated: true` from `query_subgraph`.
