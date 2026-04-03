# Test: entity extraction, relationship mapping, traversal, subgraph query, path reasoning

## Scenario

From a short corporate memo, the agent extracts organizations and services, maps an ownership/dependency edge, traverses from a project seed to find dependent services, queries a typed neighborhood subgraph, and explains the dependency path to the user.

## Given

- Document `doc_memo_14` text mentions: “Project Aurora is part of the Payments program, which owns the payments-api service.”
- Graph is initially empty except for global type constraints enforced by the store.
- Predicate allowlist for traversal includes `PART_OF`, `OWNS_SERVICE`, `DEPENDS_ON`.

## When

- The agent calls `extract_entities` with `document_ref: doc_memo_14` and appropriate `entity_types`.
- The agent calls `map_relationships` linking `Project Aurora` to `Payments program` and `Payments program` to `payments-api` with evidence spans.
- The agent upserts or confirms graph writes per integrator (out of band); then calls `traverse_graph` with seed `ent_proj_aurora`, `max_hops: 4`, `allowed_predicates: ["PART_OF", "OWNS_SERVICE"]`.
- The agent calls `query_subgraph` with `pattern: typed_neighborhood` around `ent_payments_api` with a small `limit`.
- The agent calls `reason_over_path` with the user question “Why is payments-api relevant to Project Aurora?” and `context.edges` from traversal results.

## Then

- Extracted entities include **Project**, **Program**, and **Service** types with non-overlapping canonical ids.
- At least one mapped edge has `predicate` in `{"PART_OF", "OWNS_SERVICE"}` with `confidence` above the deployment threshold or is quarantined with explicit `rejected` entries—not silently dropped.
- Traversal returns a path connecting `ent_proj_aurora` to `ent_payments_api` in the harness fixture graph.
- `reason_over_path.answer` cites only edges present in `context.edges` or explicitly marked inferred via `ruleset_ref` outcomes.
- `support_paths` is non-empty and lists edge ids matching the graph records.
