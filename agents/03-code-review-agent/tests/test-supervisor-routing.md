# Test: Supervisor routes to all sub-reviewers

## Scenario

A PR diff modifies 3 files: a Python API handler, a SQL migration, and a CSS stylesheet.

## Input

Provide a diff containing:
- `api/handlers/user.py` — adds a new endpoint with raw SQL query
- `migrations/003_add_index.sql` — adds a database index
- `frontend/styles/button.css` — changes button colors

## Expected behavior

1. The supervisor routes to ALL THREE sub-reviewers (security, style, logic) — not just one.
2. The security reviewer flags the raw SQL query as a potential injection risk.
3. The style reviewer comments on the CSS changes.
4. The logic reviewer examines the API handler control flow.
5. merge_findings is called exactly once with results from all three.
6. The final report is ordered by severity, with the SQL injection finding ranked highest.

## Failure conditions

- Supervisor skips a sub-reviewer: FAIL
- Findings are not deduplicated: FAIL
- SQL injection is not flagged: FAIL
- Report is not severity-ordered: FAIL
