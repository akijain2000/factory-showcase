# Test: entity resolution conflict, graph cycle, empty subgraph query

## Scenario

Regression triple: (1) two surface forms resolve to competing canonical entities; (2) traversal encounters a cycle in the graph and must terminate safely; (3) `query_subgraph` returns an empty result set and the agent must not hallucinate content.

## Setup

- Agent config: entity resolver threshold `0.82`, max cycle visits per node `1`, empty-result policy `acknowledge_empty`.
- Tools mocked:
  - `extract_entities` → returns mentions `"Apple Inc"` and `"Apple"` both mapping candidates to ids `ent_apple_corp` and `ent_apple_fruit` with close scores → `{ "ok": true, "ambiguity": [{ "surface": "Apple", "candidates": ["ent_apple_corp","ent_apple_fruit"] }] }`
  - `map_relationships` → on conflicting canonical choice without disambiguation, returns `{ "ok": false, "error": "ENTITY_RESOLUTION_CONFLICT", "candidates": ["ent_apple_corp","ent_apple_fruit"] }`
  - `traverse_graph` → graph contains cycle `A DEPENDS_ON B DEPENDS_ON C DEPENDS_ON A`; mock returns `{ "ok": true, "paths": [], "visited_limits": { "cycle_stopped": true } }` or explicit `CYCLE_DETECTED` per harness.
  - `query_subgraph` with pattern `typed_neighborhood` around nonexistent id → `{ "ok": true, "nodes": [], "edges": [], "empty": true }`
  - `reason_over_path` → when no paths, `{ "ok": true, "answer": "No grounded path found.", "support_paths": [] }`

## Steps

1. User sends: "From this sentence 'Apple shipped  tons of fruit to Apple stores', map ownership edges."
2. Agent should: call `extract_entities`, observe ambiguity; ask clarifying question or disambiguate using type cues before `map_relationships`.
3. Agent should: if proceeding without disambiguation, `map_relationships` returns `ENTITY_RESOLUTION_CONFLICT`; agent surfaces candidate ids and asks user to pick.
4. User sends: "Traverse dependencies from node A until you find root—graph may cycle."
5. Agent should: call `traverse_graph` with bounded hops; accept `cycle_stopped` / `CYCLE_DETECTED` outcome and explain cycle termination to user without infinite expansion.
6. User sends: "Query typed neighborhood around ent_missing_404 limit 20."
7. Agent should: call `query_subgraph`, receive empty result; acknowledge empty graph region without inventing nodes or edges.
8. User sends: "Summarize key suppliers anyway."
9. Agent should: call `reason_over_path` only with available context; with empty subgraph, return no grounded suppliers list or explicitly state insufficient data.

## Expected outcome

- Ambiguous "Apple" never maps to both corp and fruit simultaneously without user resolution.
- Traversal report mentions cycle handling rather than claiming a unique root incorrectly.
- Empty subgraph query yields explicit "no data" messaging, not fabricated entity names.

## Pass criteria

- Harness: either user clarification turn exists OR `ENTITY_RESOLUTION_CONFLICT` logged once before successful mapping.
- Traversal mock shows cycle guard triggered (`cycle_stopped` or `CYCLE_DETECTED`) exactly once in cycle scenario.
- `query_subgraph` empty case: assistant answer contains no new proper-noun suppliers absent from tool JSON.
