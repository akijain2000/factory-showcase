---
name: 02-api-endpoint-reviewer
description: Evaluates REST HTTP endpoint implementations against common design and safety checks. Use when reviewing routes, controllers, or API changes before merge.
---

# REST endpoint review

## Scope

Applies to HTTP JSON APIs using resource-oriented paths (REST-style). Adapt verbs and status guidance if the stack maps differently (e.g. RPC-over-HTTP), but keep the same safety and consistency checks.

## Workflow

1. **Locate the surface** — Identify route definition, controller entrypoint, request/response types or schemas, auth middleware, and persistence calls for the endpoint under review.
2. **Map to HTTP semantics** — Confirm method matches intent (`GET` safe/idempotent, `PUT` vs `PATCH`, `POST` for creation or actions, `DELETE` expectations). Flag misuse of success codes (`200` vs `201` vs `204`).
3. **Validate contracts** — Check path params, query validation, request body schema, content type, pagination/filter limits, and response shape stability (including error payloads).
4. **Authn and authz** — Verify authentication is required where needed, authorization checks occur after identity resolution, and object-level access is enforced (no IDOR gaps).
5. **Data and side effects** — Trace database or external calls for transaction boundaries, idempotency for mutating operations where duplicates are costly, and leakage of internal errors to clients.
6. **Observability** — Confirm structured logging, correlation IDs where the codebase supports them, and metrics or tracing hooks for failures and latency outliers.
7. **Rate and abuse limits** — Note absence of throttling, payload size limits, or file upload constraints when the endpoint is exposed on the public internet.

## Output template

Paste one row per check. `Evidence` cites file:line or the registered function name for the route.

| Check | Pass/Fail | Notes | Evidence |
| --- | --- | --- | --- |
| Method and path match resource semantics | | | |
| Status codes and error model consistent | | | |
| Input validation and schema alignment | | | |
| Authn/authz including object scope | | | |
| Idempotency / duplicate safety (if mutating) | | | |
| Pagination/filter bounds (if list/search) | | | |
| No sensitive data in responses or logs | | | |
| Performance N+1 or missing indexes called out | | | |

**Verdict:** `APPROVE` / `REQUEST_CHANGES` — one sentence rationale.

## Gotchas

- **Fat controllers** — Controller code that embeds SQL, HTTP client calls, and policy in one block hides test gaps; failures often cluster around untested branches.
- **201 without `Location`** — Creation endpoints should return a `Location` header or a clear self URL in the body when clients rely on discovery.
- **Silent coercion** — Accepting extra JSON fields without validation can mask client bugs; rejecting unknown fields is safer for public APIs.
- **Soft deletes vs `DELETE`** — Returning `404` for soft-deleted rows without documenting the behavior confuses caches and clients; align status and body with product rules.
- **Implicit ordering** — List endpoints without documented sort order change behavior when indexes shift; pin default sort and document tie-breakers.
- **Error shape drift** — Different controller paths returning different error JSON keys breaks generic clients; enforce one envelope via shared middleware or a single error-mapping module in the codebase.

## Hand-off

If `REQUEST_CHANGES`, list concrete edits (file or module names), ordered by severity: security, correctness, contract, then polish.
