# API Test Generator Agent

**Pattern:** Tool-heavy OpenAPI → executable test suite  
**Goal:** Parse specifications, emit deterministic test cases, validate responses against schemas, run tests, mock dependencies, and produce human-readable reports.

## Architecture

The pipeline is strictly ordered: **parse** → **generate** → **validate** (static) → **mock** (if needed) → **run** → **report**. Structured outputs (JSON/YAML) flow between stages so CI can diff artifacts.

```
   +---------------+
   |  OpenAPI doc  |
   +-------+-------+
           |
   +-------v-------+
   | parse_openapi |
   +-------+-------+
           |
   +-------v------------+      +------------------------+
   | generate_test_case |----->| validate_response_schema|
   +-------+------------+      +-----------+------------+
           |                                 |
   +-------v-------+                (per case)
   |  mock_endpoint | (optional)
   +-------+-------+
           |
   +-------v-------+
   |   run_test    |
   +-------+-------+
           |
   +-------v-------+
   | generate_report|
   +----------------+
```

**Structured output contract:** Generated test files **must** be valid for the project’s runner (e.g., pytest + requests, or k6) and include stable ids for flake tracking.

## Contents

| Path | Purpose |
|------|---------|
| `system-prompt.md` | Schema-first generation **rules** |
| `tools/` | Six tool specifications |
| `tests/` | Behavioral scenario |
| `src/` | Generator skeleton |
