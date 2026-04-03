---
name: s20-knowledge-graph-reasoning
description: Extracts entities and relations from text then traverses graphs for multi-hop answers. Use when facts span documents and tabular joins miss implicit links for agent 20-knowledge-graph.
---

# Entity extraction and graph traversal

## Goal / overview

Turn unstructured mentions into nodes and edges, normalize identifiers, and walk the graph with bounded depth to answer relational questions. Pairs with **agent 20-knowledge-graph**.

## When to use

- Answers require chaining (person → works_at → project → uses_tech) across sources.
- Tables exist but many relationships appear only in prose.
- Duplicate names and aliases appear and must be resolved before traversal.

## Steps

1. **Ingest**: Segment source text into passages with stable source IDs (file, URL, row id).
2. **Extract**: For each passage, list candidate entities (typed: person, org, product, location, concept) and relation triples `(subject, predicate, object)` with confidence.
3. **Entity confidence**: Assign an extraction confidence score to each entity (not only to triples). When traversing the graph, **propagate** combined confidence along paths (e.g. multiply or take the minimum of edge and node scores per hop). **Flag** answers and paths whose aggregate confidence falls below a defined threshold so they can be verified or disclaimed.
4. **Normalize**: Map surface forms to canonical node IDs; merge synonyms using a dictionary or embedding similarity with a human-approved threshold for auto-merge.
5. **Build / update**: Upsert nodes and edges; store provenance on each edge (source passage, extractor version). Retain contradictory edges with timestamps instead of silent overwrite.
6. **Query**: Translate the question into a pattern (e.g. 2-hop path, constrained subgraph). Apply depth and fan-out limits to avoid blow-up.
7. **Answer**: Return the path or subgraph used, ranked by support (count of independent sources). If under-specified, list what extra entity or relation is missing.

## Output format

```markdown
## Graph slice

Subgraph grounded in sources for the current question—nodes, edges, traversal pattern, and the answer path with provenance.

### Nodes
| id | type | label | aliases |

### Edges
| src | predicate | dst | provenance |

### Query pattern
- ...

### Traversal result
- Paths:
- Support scores:

### Answer
- ...
```

## Gotchas

- High-confidence wrong merges propagate errors; keep a review queue for entity pairs above similarity but below certainty.
- Popular hub nodes explode breadth-first search; use typed filters on edges.
- Extractors hallucinate relations; require at least one textual span per triple for audit.

## Test scenarios

1. **Activation**: From two short bios, extract entities and assert a `(person)-[works_at]->(org)` edge with both source IDs on the edge.
2. **Workflow**: Answer "Which tech does Alice's employer sponsor?" with a two-hop traversal and show the intermediate org node.
3. **Edge case**: When two companies share a name, return two disconnected subgraphs and ask for a disambiguator instead of merging blindly.
