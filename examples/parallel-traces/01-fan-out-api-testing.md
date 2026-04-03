# Parallel Trace: Fan-Out API Testing

Worked example showing how agent 16-parallel-executor fans out API test generation across multiple endpoints, collects traces, and merges results with partial failure handling.

## Scenario

An OpenAPI spec with 12 endpoints across 3 resources (users, orders, products). The agent generates tests for all endpoints in parallel waves.

## Trace

```
trace_id: tr-api-test-001
correlation_id: corr-openapi-batch-7

[T+0ms] set_concurrency_limit
  input:  { max_concurrent: 4 }
  output: { previous: 8, current: 4, reason: "staging cluster has 4 cores" }

[T+50ms] fan_out
  input: {
    correlation_id: "corr-openapi-batch-7",
    shards: [
      { id: "shard-users-crud",    payload: { resource: "users",    endpoints: ["GET /users", "POST /users", "GET /users/:id", "PUT /users/:id"] }},
      { id: "shard-orders-crud",   payload: { resource: "orders",   endpoints: ["GET /orders", "POST /orders", "GET /orders/:id"] }},
      { id: "shard-products-crud", payload: { resource: "products", endpoints: ["GET /products", "POST /products", "GET /products/:id", "PUT /products/:id", "DELETE /products/:id"] }}
    ]
  }
  output: {
    dispatched: 3,
    wave: 1,
    branch_ids: ["br-001", "br-002", "br-003"]
  }

[T+2100ms] shard-users-crud COMPLETED (br-001)
  tests_generated: 8, duration_ms: 2050

[T+2400ms] shard-products-crud COMPLETED (br-003)
  tests_generated: 12, duration_ms: 2350

[T+5200ms] shard-orders-crud FAILED (br-002)
  error: "Schema ref $ref '#/components/schemas/OrderItem' not found"
  duration_ms: 5150

[T+5250ms] trace_aggregate
  input: { branch_ids: ["br-001", "br-002", "br-003"], include_metadata: true }
  output: {
    total_duration_ms: 5200,
    succeeded: 2,
    failed: 1,
    spans: [
      { branch: "br-001", status: "ok", duration_ms: 2050 },
      { branch: "br-002", status: "error", duration_ms: 5150, error: "missing schema ref" },
      { branch: "br-003", status: "ok", duration_ms: 2350 }
    ]
  }

[T+5300ms] handle_partial_failure
  input: {
    failed_branches: ["br-002"],
    policy: "continue_with_partial"
  }
  output: {
    action: "continue_with_partial",
    excluded: ["shard-orders-crud"],
    note: "Orders tests skipped due to broken schema reference"
  }

[T+5350ms] fan_in
  input: {
    correlation_id: "corr-openapi-batch-7",
    merge_strategy: "concat",
    sort_key: "shard_index"
  }
  output: {
    merged_tests: 20,
    coverage: { users: "4/4 endpoints", products: "5/5 endpoints", orders: "0/3 endpoints (excluded)" },
    warnings: ["Orders resource excluded due to schema error"]
  }
```

## Key Patterns Demonstrated

1. **Concurrency limit before fan-out**: Always set limits based on infrastructure capacity
2. **Stable ordering in merge**: `sort_key: shard_index` ensures deterministic test file output
3. **Partial failure policy**: `continue_with_partial` produces useful output even when one shard fails
4. **Trace aggregation**: Unified timeline with per-branch status enables debugging
