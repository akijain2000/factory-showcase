---
name: s05-database-safety-gates
description: Defines human confirmation steps and guards for destructive or high-blast-radius database work. Use when DDL touches production, bulk deletes run, or agent 05-db-admin-agent proposes schema changes.
---

# Database safety gates and human confirmation

## Goal / overview

Ensure destructive or wide-impact database operations never run on reflex: explicit scope, environment checks, and human-in-the-loop (HITL) gates where policy requires. Pairs with agent `05-db-admin-agent`.

## When to use

- Scripts include `DROP`, `TRUNCATE`, mass `DELETE`, or `ALTER` that locks large tables.
- Connections might point at production despite intent to use a staging clone.
- Runbooks grant agents power to execute SQL against shared clusters.

## Steps

1. **Classify the operation**: read-only query vs schema change vs data mutation vs privilege change; note estimated rows or table sizes when the catalog allows.
2. **Verify target environment**: require explicit connection target (host, database name, role); block or warn on prod-like hostnames unless a named override flag is present.
3. **Scope statement**: restate object names, predicates, and time window; reject ambiguous patterns (`DELETE FROM users` without `WHERE`).
4. **HITL checkpoint**: for classified-high-risk actions, pause for typed confirmation (e.g. environment name + ticket id) or approver token per org policy; log the gate result.
5. **Dry-run or shadow path**: prefer `EXPLAIN`, transaction rollback in a session, or replica read-only verification before final commit.
6. **Post-action verification**: row counts, constraint checks, application health metrics; define rollback (restore point, inverse migration, feature flag) before execution.

## Output format

- **Risk card**: operation class, objects, environment, blast-radius estimate, gate required (yes/no).
- **Execution bundle**: ordered SQL or migration steps with each step labeled pre-approved or needs HITL.
- **Audit snippet**: what was confirmed, by which mechanism, and timestamp fields for logs.

## Gotchas

- Cascading deletes and foreign keys can amplify a small-looking `DELETE`; trace FK graphs before approval.
- Long-running locks during peak traffic are a production incident; schedule or use online schema tools when available.
- A "staging" database restored from prod may still hold real PII—treat credentials and exports with the same care as prod.

## Test scenarios

1. **Ambitious DELETE**: Proposed statement lacks a limiting predicate; gate should refuse until a scoped `WHERE` and row-count estimate appear.
2. **Prod-looking URL**: Connection string host matches production pattern; gate should require explicit override and HITL even if the operator claims staging.
3. **Additive vs destructive mix**: Migration file adds a column and drops an index; output should split gates—fast path for additive, HITL for destructive—and order steps safely.
