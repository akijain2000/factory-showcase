---
name: s08-api-test-generation
description: Parses OpenAPI descriptions and scaffolds executable tests for endpoints and schemas. Use when coverage for HTTP APIs is thin or the api-test-generator agent needs a baseline suite.
---

# API test generation from OpenAPI

## Goal / overview

Turn an OpenAPI document into a structured test plan and starter tests that validate status codes, schemas, and representative happy paths. Pairs with agent `08-api-test-generator`.

## When to use

- A service ships an OpenAPI spec but lacks automated contract checks.
- Refactors risk silent response shape changes.
- New endpoints need default negative cases (401/403/404/422).

## Steps

1. Validate the OpenAPI file: version, server URLs, security schemes, and referenced components resolve.
2. Build an endpoint index: method, path, operationId, auth requirements, request body schema, response schemas by status.
3. For each operation, pick cases: **happy path**, **auth missing/invalid** (when security exists), **validation failure** (required fields absent or wrong type), **not found** for resource routes.
4. **Edge cases**: Where the schema or operation allows it, add tests for **empty arrays**, **null or omitted optional fields**, and **boundary values** (min/max numeric, min/max length strings, enum edges). Include **auth failures** beyond the baseline (wrong scheme, expired token) when security is documented. Cover **rate limiting** (e.g. 429) when the spec or platform documents limits; use mocks or sandboxes so CI does not trip real throttles.
5. Map schemas to example fixtures: reuse spec examples when present; otherwise synthesize minimal valid payloads respecting `required` and formats.
6. Emit test scaffolding in the project’s test runner style (e.g. Jest, pytest, Go test tables) with TODO markers for business assertions.
7. Add shared helpers for auth header injection and base URL configuration from environment variables.

## Output format

- **Coverage matrix**: operationId × case type × expected status.
- **Generated files list**: paths created or modified.
- **Fixture notes**: which examples are spec-backed vs synthetic.

## Gotchas

- Specs drift from implementation; mark tests that need manual verification against a running server.
- Polymorphic or `oneOf` schemas need explicit example selection; avoid guessing illegal combinations.
- Rate limits and side effects (payments, deletes) belong behind test doubles or dedicated sandboxes.

## Test scenarios

1. **Bearer-secured CRUD**: Spec lists GET/POST with 401 without token; scaffold should include auth negative and positive cases.
2. **Undocumented 500**: Spec only defines 200; scaffold should still add a placeholder for error-path observation without asserting undocumented bodies.
3. **Broken ref**: Component `$ref` missing; parser should stop with a clear file/line reference instead of emitting partial tests.
