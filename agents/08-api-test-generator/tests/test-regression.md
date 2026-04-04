# Test: Regression — invalid OpenAPI, deprecated endpoints, auth-required routes

## Scenario

Real specs are messy: invalid OpenAPI, deprecated operations, and endpoints that require auth. The suite must still be safe, accurate, and runnable with mocks—not silently skip auth or treat deprecated paths as first-class without warning.

## Setup

- Agent config: `deprecation_warning_level: warn`, `require_auth_mock_when_security: true`
- Tools mocked:
  - `parse_openapi` → `{ valid: false, errors: ["components.schemas.User missing $ref target"] }` for broken spec variant A
  - `parse_openapi` → variant B returns operations including `{ path: "/legacy/ping", deprecated: true, security: [] }` and `{ path: "/users/me", deprecated: false, security: [{ bearerAuth: [] }] }`
  - `generate_test_case` → tags tests with `deprecated: true` when operation flagged
  - `validate_response_schema` → skips with reason when response has no declared schema
  - `mock_endpoint` → provides bearer token exchange for `/oauth/token`
  - `run_test` → without mock for secured route returns `401` once; with mock returns `200`

## Steps

1. User sends: "Parse this OpenAPI—it's a bit broken—and generate tests anyway."
2. Agent should: call `parse_openapi`; on `valid: false`, report blocking errors; propose minimal fix or stop—**no** pretend full operation list.
3. User sends: "Use variant B only: cover `/legacy/ping` and `/users/me`."
4. Agent should: generate test for deprecated `/legacy/ping` with visible deprecation warning in summary; avoid treating as recommended API.
5. Agent should: for `/users/me`, call `mock_endpoint` or document required bearer setup **before** expecting `200`.
6. Agent should: call `run_test`; interpret first `401` as signal to add auth mock, then rerun once.

## Expected outcome

- Invalid spec does not yield hallucinated paths or schemas.
- Deprecated operations are labeled in agent output and tests metadata.
- Auth-required routes get mocks or skipped runs with explicit reason—no false green.

## Pass criteria

- When spec invalid, zero `generate_test_case` calls for operations not returned by `parse_openapi`.
- Test plan mentions deprecation for `/legacy/ping`.
- Sequence includes auth mock or equivalent before final successful `run_test` for secured route in the corrected branch.
