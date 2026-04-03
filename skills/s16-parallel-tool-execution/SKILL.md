---
name: s16-parallel-tool-execution
description: Processes independent tool calls in parallel and aggregates results into one trace. Use when latency matters and calls have no hidden dependencies for agent 16-parallel-executor.
---

# Fan-out, fan-in, and trace aggregation

## Goal / overview

Run safe parallel tool calls, preserve causal ordering in the trace, and fold results back into a single coherent response. Pairs with **agent 16-parallel-executor**.

## When to use

- Several reads or lookups touch different resources with no write ordering requirement.
- Wall-clock time dominates and the orchestrator can issue N calls at once.
- Observability must show which branch produced which evidence.

## Steps

1. **Dependency check**: Build a directed graph of tool calls. Only fan out nodes with in-degree satisfied and no read-after-write hazard on mutable state.
2. **Batch**: Group independent calls into a wave. Assign each call a stable `branch_id` and shared `parent_span_id`.
3. **Execute**: Launch the wave in parallel with a global deadline. Cancel or detach stragglers per policy (abort all vs best-effort).
4. **Collect**: Gather results keyed by `branch_id`. Normalize errors into a struct: `code`, `message`, `retryable`.
5. **Aggregate**: Apply fan-in logic—merge lists, vote on booleans, or reduce with a defined combiner. Preserve ordering only where the user-facing narrative requires it.
6. **Trace**: Emit one summary span listing branches, durations, and outcome counts; attach child spans per branch without cross-mixing payloads.

## Output format

```markdown
## Parallel wave

One batch of concurrent tool calls with explicit dependency edges, per-branch outcomes, and how results merge for the user or downstream steps.

### Graph
- Nodes: ...
- Edges: ...

### Wave execution
| branch_id | tool | status | duration_ms |

### Fan-in result
- ...

### Trace summary
- parent_span_id:
- children:
- errors:
```

## Gotchas

- Parallel writes to the same key without serialization invites races; serialize or use compare-and-swap.
- Tools with hidden session side effects are not independent even if inputs differ; treat them as sequential.
- Aggregating traces by string sort on timestamps breaks when clocks skew; use logical sequence numbers.

## Test scenarios

1. **Activation**: Plan three read-only HTTP fetches in one wave; show `branch_id` assignment and merged JSON array output.
2. **Workflow**: When one branch fails with a retryable error and two succeed, specify whether to retry only the failed branch or rerun the wave.
3. **Edge case**: If call B needs a token returned from call A, redraw the graph as two waves and explain why parallel execution is invalid.
