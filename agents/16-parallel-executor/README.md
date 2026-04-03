# Parallel Executor Agent

Runs independent subtasks concurrently, collects per-branch traces, and merges results with partial-failure recovery so the parent workflow can continue when some branches fail.

## Audience

- **Platform engineers** wiring multi-tool fan-out in agent runtimes.
- **Agent authors** who need deterministic merge semantics and traceable concurrency.
- **Operators** tuning worker pools, timeouts, and retry policies without changing task logic.

## Quickstart

1. Define a task bundle (ordered or keyed subtasks) and optional branch metadata.
2. Point the executor at your dispatcher config (worker count, per-branch timeout, merge strategy).
3. Invoke the agent; partial failures surface as `failed_branches` while successful branches merge into the combined result.
4. Inspect the unified trace via `trace_aggregate` for timelines and branch correlation.

```text
# Example invocation (conceptual)
parallel_executor.run(
  task_id="batch-001",
  branches=[{ "id": "a", "tool": "fetch" }, { "id": "b", "tool": "summarize" }],
  merge="fan_in_with_partial_ok"
)
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PARALLEL_EXECUTOR_MAX_WORKERS` | Upper bound on concurrent branch executions | `8` |
| `PARALLEL_EXECUTOR_BRANCH_TIMEOUT_MS` | Per-branch wall-clock limit | `60000` |
| `PARALLEL_EXECUTOR_MERGE_STRATEGY` | `all_or_nothing`, `partial_ok`, or `first_success` | `partial_ok` |
| `PARALLEL_EXECUTOR_TRACE_RETENTION` | How many completed runs to retain traces for | `100` |
| `PARALLEL_EXECUTOR_RETRY_ATTEMPTS` | Retries for transient branch failures | `2` |
| `PARALLEL_EXECUTOR_LOG_LEVEL` | Logging verbosity for dispatcher and workers | `info` |

## Architecture

High-level data flow with partial failure recovery at fan-in:

```text
                    +------------------+
                    |      Task        |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Fan-out          |
                    | dispatcher       |
                    +--------+---------+
                             |
           +-----------------+-----------------+
           |                 |                 |
           v                 v                 v
    +------------+   +------------+   +------------+
    | Worker 1   |   | Worker 2   |   | Worker N   |
    | (branch)   |   | (branch)   |   | (branch)   |
    +------+-----+   +------+-----+   +------+-----+
           |                 |                 |
           +-----------------+-----------------+
                             |
                             v
                    +------------------+
                    | Trace collector  |
                    | (branch IDs)     |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Fan-in merger    |
                    | + partial        |
                    |   failure        |
                    |   recovery       |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Merged result +  |
                    | unified trace    |
                    +------------------+
```

**Flow:** The dispatcher assigns each branch to a worker pool slot. The trace collector records start/end, errors, and tool spans per `branch_id`. The fan-in merger applies the configured strategy: successful branches contribute to the payload; failed branches are listed for retry or downstream handling without aborting the whole run when `partial_ok` is enabled.

## Testing

- **Unit:** Mock workers with fixed latency and injected failures; assert merge output and `failed_branches` cardinality.
- **Integration:** Run against a stub tool server; verify trace ordering and that `trace_aggregate` timelines align with wall-clock ordering per branch.
- **Chaos:** Random worker timeouts; confirm partial recovery and that `all_or_nothing` aborts the batch as expected.
- **Load:** Saturate `PARALLEL_EXECUTOR_MAX_WORKERS` and confirm backpressure and no trace loss under retention limits.

## Related files

- `tools/trace_aggregate.md` — unified timeline from concurrent tool traces
- Agent orchestration hooks (if present): `parallel_executor.yaml` / runtime adapter in your stack
- Parent factory-showcase index listing agent `16-parallel-executor`
