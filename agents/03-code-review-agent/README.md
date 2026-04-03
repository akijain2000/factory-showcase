# Code Review Agent

Multi-agent code review system using a supervisor pattern to coordinate specialized sub-reviewers for security, style, and logic analysis.

## Architecture

```
                    ┌──────────────┐
                    │  Supervisor  │
                    │  (router)    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  Security  │ │   Style    │ │   Logic    │
     │  Reviewer  │ │  Reviewer  │ │  Reviewer  │
     └────────────┘ └────────────┘ └────────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │   Merge      │
                    │   Findings   │
                    └──────────────┘
```

The supervisor receives the diff, routes it to all three sub-reviewers in parallel, collects findings, deduplicates overlapping issues, and produces a unified review report ranked by severity.

## Tools

- `handoff_to_subagent` — Route diff to a specialized reviewer
- `merge_findings` — Combine and deduplicate results from sub-reviewers
- `scan_secrets` — Detect credential patterns in diffs
- `check_injection_patterns` — Identify injection vulnerabilities
- `lint_style_conventions` — Check code style compliance
- `analyze_control_flow` — Detect logic bugs and unreachable code

## Quickstart

```bash
python src/agent.py --diff path/to/diff.patch
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MODEL_API_KEY` | Yes | Model API key (set in environment, not in code) |
| `REVIEW_MAX_FILES` | No | Max files to review per run (default: 50) |
| `REVIEW_SEVERITY_THRESHOLD` | No | Minimum severity to report: low, medium, high (default: low) |
