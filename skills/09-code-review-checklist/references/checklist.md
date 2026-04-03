# Detailed code review checklist

Use this file after the workflow in the parent `SKILL.md`. Check items that apply to the diff; mark others `N/A` with a short reason.

## Table of contents

1. [Security](#security)
2. [Secrets and configuration](#secrets-and-configuration)
3. [Privacy and compliance](#privacy-and-compliance)
4. [Authentication and authorization](#authentication-and-authorization)
5. [Input validation and injection](#input-validation-and-injection)
6. [APIs and contracts](#apis-and-contracts)
7. [Error handling and observability](#error-handling-and-observability)
8. [Concurrency and parallelism](#concurrency-and-parallelism)
9. [Performance](#performance)
10. [Resource usage and limits](#resource-usage-and-limits)
11. [Data and persistence](#data-and-persistence)
12. [Readability and maintainability](#readability-and-maintainability)
13. [Testing](#testing)
14. [Dependencies and supply chain](#dependencies-and-supply-chain)
15. [Documentation and user-facing copy](#documentation-and-user-facing-copy)
16. [Rollback and operability](#rollback-and-operability)

---

## Security

- [ ] Trust boundaries are explicit (who can call what, with which credentials).
- [ ] New surface area is authenticated where required; anonymous access is intentional and documented.
- [ ] Authorization checks occur after authentication and use the same identity source as the rest of the app.
- [ ] Sensitive operations require more than a single weak factor (tokens, cookies, headers) unless documented.
- [ ] File uploads and path operations cannot escape intended directories.
- [ ] Deserialization of untrusted data uses safe parsers or explicit schemas.
- [ ] Redirects and forward URLs cannot be abused for open redirects.
- [ ] Rate limiting or abuse controls are considered for new public endpoints.
- [ ] Security-sensitive errors do not leak stack traces or internal IDs to clients.
- [ ] Dependencies with known CVEs are not introduced without a documented exception path.

## Secrets and configuration

- [ ] No secrets, tokens, or private keys appear in code, tests, or fixtures committed to the repo.
- [ ] Configuration defaults are safe in production (no debug flags, no permissive CORS, no open admin).
- [ ] Environment-specific values are loaded from environment or secret stores, not hard-coded.
- [ ] Feature flags default to the safer state when misconfigured.
- [ ] Rotation and expiry are considered for new long-lived credentials.

## Privacy and compliance

- [ ] Personal data collection is minimized and purpose-limited.
- [ ] Logs and metrics do not record passwords, full payment details, or health data unless required and approved.
- [ ] Data retention and deletion paths are consistent with policy.
- [ ] Cross-border or vendor subprocessors are noted if data leaves the primary region.

## Authentication and authorization

- [ ] Session and token lifetimes match product expectations.
- [ ] Logout and token revocation behavior is correct for the auth model.
- [ ] Role or permission changes take effect without stale cached grants, or caching is bounded and documented.
- [ ] Privilege escalation paths (self-signup to admin, IDOR) are closed.

## Input validation and injection

- [ ] All external inputs are validated for type, length, and allowed values where relevant.
- [ ] SQL uses parameterization or an equivalent safe API.
- [ ] HTML output is escaped or sanitized when rendering user content.
- [ ] Shell commands are not built from unchecked strings.
- [ ] Regular expressions are safe from catastrophic backtracking on hostile input.

## APIs and contracts

- [ ] Public request and response shapes are backward compatible or versioned.
- [ ] Error codes and messages are stable enough for clients to rely on.
- [ ] Pagination, sorting, and filtering behave deterministically.
- [ ] Idempotency keys or duplicate protection exist for mutating operations that need them.
- [ ] Deprecations include timelines and migration notes.

## Error handling and observability

- [ ] Errors are logged with enough context to debug (request id, user id where appropriate) without leaking secrets.
- [ ] Fatal paths release resources (connections, locks, temp files).
- [ ] Metrics or traces cover new critical paths.
- [ ] Alert noise is considered: new errors should be actionable.

## Concurrency and parallelism

- [ ] Shared mutable state is guarded correctly (locks, atomics, message passing).
- [ ] Deadlocks and lock ordering are safe under nested calls.
- [ ] Goroutines, threads, or async tasks cannot leak on shutdown.
- [ ] Timeouts exist on network and external service calls.

## Performance

- [ ] Hot loops avoid unnecessary allocations or repeated parsing.
- [ ] N+1 query patterns are not introduced; batching or joins are used where needed.
- [ ] Caching keys include all dimensions that affect correctness.
- [ ] Large payloads use streaming or chunking where appropriate.
- [ ] Algorithmic complexity is appropriate for expected input size.

## Resource usage and limits

- [ ] Memory use is bounded for unbounded inputs (streams, iterators, caps).
- [ ] Disk and temp file usage is cleaned up on success and failure.
- [ ] Connection pools are sized and not exhausted by happy-path leaks.
- [ ] Background jobs have retry and backoff that will not stampede dependencies.

## Data and persistence

- [ ] Migrations are reversible or paired with a documented rollback.
- [ ] Transactions cover related writes; partial updates cannot corrupt invariants.
- [ ] Indexes support new query patterns without full table scans at expected scale.
- [ ] Nullable columns and defaults are intentional.
- [ ] Soft deletes versus hard deletes match product and compliance needs.

## Readability and maintainability

- [ ] Names reflect behavior, not history or jokes.
- [ ] Functions are short enough to reason about; deep nesting is reduced.
- [ ] Magic numbers are named constants with units where helpful.
- [ ] Comments explain why, not what, unless the code is unavoidably obscure.
- [ ] Duplication is acceptable only when abstraction would obscure differences.

## Testing

- [ ] New behavior has automated coverage at the right layer (unit, integration, e2e).
- [ ] Edge cases include empty input, max size, and failure of dependencies.
- [ ] Tests are deterministic (no wall-clock races without control).
- [ ] Flaky patterns (sleep, unordered map iteration as contract) are avoided.
- [ ] Test data does not depend on global shared state unless isolated.

## Dependencies and supply chain

- [ ] New dependencies are justified by capability, not convenience alone.
- [ ] License compatibility is acceptable for the product.
- [ ] Pin versions or lockfiles are updated consistently.
- [ ] Transitive risk is noted for high-impact libraries (crypto, parsing, networking).

## Documentation and user-facing copy

- [ ] README or operator docs change when behavior or setup changes.
- [ ] User-visible strings are clear, actionable, and localized if the product localizes.
- [ ] Breaking changes appear in changelog or release notes.

## Rollback and operability

- [ ] Rollback steps are documented for schema, config, and binary changes.
- [ ] Feature flags or kill switches exist for risky launches when appropriate.
- [ ] Runbooks mention new failure modes and dashboards.
- [ ] On-call impact is assessed (pages, severity, noise).

---

## How to record results

For each section touched by the diff, paste the section heading into the review and list failed items with file references. Sections with no applicable items can be omitted or marked `N/A` in one line.
