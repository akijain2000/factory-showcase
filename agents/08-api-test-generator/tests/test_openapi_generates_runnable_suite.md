# Behavioral test: OpenAPI → runnable suite

## Scenario

1. User provides OpenAPI 3.1 file with `GET /users/{id}` returning `200` with a JSON body schema.
2. Agent **invokes** `parse_openapi` and receives `operations` including that path.
3. Agent **invokes** `generate_test_case` with `framework: pytest_requests` for that operation.
4. Agent **invokes** `validate_response_schema` for `200` and the schema ref from the spec.
5. Agent **invokes** `mock_endpoint` for an auth dependency returning `200` with a token.
6. Agent **invokes** `run_test` for the new `test_id`.
7. Agent **invokes** `generate_report` with `format: junit`.

## Expected behavior

- Generated source **must** respect **constraints**: no hardcoded production host; uses `base_url_var`.
- `validate_response_schema` runs before `run_test` when schema exists (**rules** for ordering).
- If `run_test` returns `failed`, agent surfaces `stdout_snippet` and proposes a fix—**does not** claim success.
- Report artifact path is returned and references the same `run_id`.

## Failure modes

- Skipping `validate_response_schema` when `200` has a declared body schema → **fail**
- Fewer than six distinct **tool** **invokes** when mocks and report are requested → **fail**
