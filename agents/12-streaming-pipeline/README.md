# Streaming Pipeline Agent (Event-Driven)

An agent that reasons about **unified event streams**, **interceptor chains**, **backpressure**, and **hierarchical cancellation**. It is designed for operators and runtime authors integrating high-throughput async pipelines where partial subtree teardown must not leak resources.

## Audience

Backend and platform engineers building **fan-out/fan-in** workers, streaming LLM token pipelines, or multi-stage enrichment graphs with cooperative cancellation.

## Quickstart

1. Mount `system-prompt.md` in your orchestrator.
2. Implement tools per `tools/*.md` against your event bus and telemetry.
3. Use `src/agent.py` as a reference for ordering: emit → intercept → aggregate → consume, with cancel propagation.

## Configuration

| Variable | Description |
|----------|-------------|
| `EVENT_BUS_ENDPOINT` | Logical or HTTP endpoint for the unified stream |
| `STREAM_ROOT_SCOPE_ID` | Default root for hierarchical cancellation |
| `BACKPRESSURE_METRICS_REF` | Where `inspect_backpressure` reads gauges |
| `MODEL_API_ENDPOINT` | Optional: agent’s own reasoning calls |

## Architecture

```
 +----------------+     emit_event      +----------------------+
 |   Producers    |-------------------->|  Unified event bus   |
 | (tasks, IO,    |                     |  (topics / partitions)|
 |  LLM chunks)   |                     +----------+-----------+
 +----------------+                                |
                                                   |  dispatch
                                                   v
                                        +----------------------+
                                        | Interceptor chain    |
                                        | (ordered middleware) |
                                        +----------+-----------+
                                                   |
                         register_interceptor ------+
                                                   |
                    +------------------------------+------------------------------+
                    |                              |                              |
                    v                              v                              v
           +----------------+            +----------------+            +----------------+
           | transform /    |            | filter / rate  |            | audit / policy |
           | enrich         |            | limit          |            | guardrails     |
           +--------+-------+            +--------+-------+            +--------+-------+
                    |                              |                              |
                    +------------------------------+------------------------------+
                                                   |
                                                   v
                                        +----------------------+
                                        | aggregate_stream     |
                                        | (windows, joins,      |
                                        |  session buffers)    |
                                        +----------+-----------+
                                                   |
                                                   v
                                        +----------------------+
                                        | Consumer(s)          |
                                        | + backpressure hooks |
                                        +----------+-----------+
                                                   |
                    cancel_subtree ----------------+
                    (propagate down scope tree)     |
                                                   v
                                        +----------------------+
                                        | Drained subtrees &   |
                                        | released buffers     |
                                        +----------------------+
```

## Failure modes

- **Backpressure:** consumers lag; interceptors must not unbounded-buffer.
- **Cancel storms:** `cancel_subtree` must be idempotent and scope-scoped.
- **Ordering:** partition keys must be explicit for `aggregate_stream`.

## Testing

See `tests/` for cancellation and interceptor ordering scenarios.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
