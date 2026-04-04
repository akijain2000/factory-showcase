# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

OpenAPI-driven test generation hits flaky services: parsing, validation, or test runs fail. The agent retries idempotent read steps, backs off on run failures, and stops calling a broken runner after a circuit opens.

## Setup

- Agent config: `max_tool_retries: 2`, `run_test_timeout_ms: 15000`, `circuit_breaker: { on_tool: "run_test", trip_after_failures: 3, reset_s: 45 }`, `base_url_var: API_BASE_URL`
- Tools mocked:
  - `parse_openapi` → attempt 1: timeout; attempt 2: `{ operations: [{ method: "GET", path: "/users/{id}", operation_id: "getUser" }] }`
  - `generate_test_case` → success `{ test_id: "t-77", framework: "pytest_requests" }`
  - `validate_response_schema` → attempt 1: `502`; attempt 2: `{ valid: true, status: "200" }`
  - `mock_endpoint` → success `{ mock_id: "m-1" }`
  - `run_test` → three failures `{ status: "failed", stdout_snippet: "Connection refused" }` then circuit open (tool returns `circuit_open: true`)
  - `generate_report` → `{ path: "reports/junit-77.xml" }` only if last `run_test` succeeded in alternate branch (not used when circuit open)

## Steps

1. User sends: "From this OpenAPI file, build a pytest request test for GET /users/{id}, validate schema, mock auth, run it, and give me JUnit."
2. Agent should: call `parse_openapi`; retry once on timeout; proceed with operations list.
3. Agent should: call `generate_test_case` then `validate_response_schema`; retry once on 502; order validation before `run_test` when schema exists.
4. Agent should: call `mock_endpoint` for auth dependency as needed.
5. Agent should: call `run_test` until circuit trips; after `circuit_open`, stop invoking `run_test`; explain failure with `stdout_snippet` evidence.
6. Agent should: call `generate_report` only if a run succeeded—otherwise skip or produce a report stub **only** if policy allows, and label it as not executed.

## Expected outcome

- Bounded retries on `parse_openapi` and `validate_response_schema`; no infinite `run_test` loop.
- User sees honest failure analysis when tests cannot reach the runner.
- No claim that JUnit exists at `reports/junit-77.xml` unless a successful run occurred per policy.

## Pass criteria

- `run_test` invocations ≤ 3 before circuit open in this mock.
- `validate_response_schema` occurs before final successful `run_test` attempt in the happy sub-path (if any); in this scenario, agent never asserts green build.
- Assistant message cites tool snippets, not invented stack traces.
