---
name: s19-workflow-dag-design
description: Models workflows as directed acyclic graphs with checkpoint and resume boundaries. Use when orchestrating long jobs, retries, or human approvals for agent 19-workflow-orchestrator.
---

# DAG step design with checkpointing

## Goal / overview

Express work as a DAG so parallel steps stay explicit, cycles are impossible by construction, and failures resume from durable checkpoints instead of from zero. Pairs with **agent 19-workflow-orchestrator**.

## When to use

- Pipelines mix automated steps, queues, and optional human gates.
- Some steps are expensive and should not rerun after transient failures.
- Different branches produce artifacts consumed by a later join node.

## Steps

1. **Decompose**: List atomic steps with inputs, outputs, idempotency keys, and estimated duration. Merge trivial micro-steps to limit graph noise.
2. **Draw edges**: Add directed edges for true dependencies only. If B needs A's artifact path, edge A→B; if B only needs a count from A, specify a smaller artifact.
3. **Acyclic check**: Verify no cycles via topological sort. If feedback loops are required, model them as new workflow instances with versioned state, not hidden graph cycles.
4. **Checkpoint placement**: After any step that mutates external state or costs > T seconds, define a checkpoint record: inputs hash, output URIs, status, error class.
5. **Failure policy**: Per edge or node, choose retry, compensate, or abort-downstream. Document partial outputs and garbage collection rules.
6. **Join semantics**: For multi-parent nodes, specify wait-for-all vs wait-for-any and how to merge partial failures.

## Output format

```markdown
## DAG: <workflow>

Executable graph for one named workflow; fill `<workflow>` so checkpoints and failure policies map to a single deployable or automatable pipeline.

### Nodes
| id | step | inputs | outputs | idempotent |

### Edges
- ...

### Checkpoints
| after node | persisted fields | TTL |

### Failure policy
- ...

### Join rules
- ...
```

## Gotchas

- Checkpoints without input hashes rerun stale work after upstream fixes; always version inputs.
- "Wait-for-any" joins need explicit handling when the losing branch later errors asynchronously.
- Human approval nodes need expiry; otherwise the graph stalls with locked resources.

## Test scenarios

1. **Activation**: Sketch a five-node DAG with two parallel branches that join before a deploy step; mark checkpoints after build and after integration tests.
2. **Workflow**: When node C fails after A and B succeeded, specify resume from C with A/B artifacts reused from checkpoint storage.
3. **Edge case**: If a dependency is soft (nice-to-have cache) vs hard (required secret), model soft deps as optional inputs with fallback paths instead of hiding failure.
