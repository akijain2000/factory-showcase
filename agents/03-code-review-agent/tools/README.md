# Tools: Code Review Agent

Supervisor tool:

- `handoff_to_subagent` — route work to `security_reviewer`, `style_reviewer`, or `logic_reviewer`
- `merge_findings` — dedupe and normalize severities

Sub-agent tools (enforced by allowlist in `src/agent.py`):

| Sub-agent | Tools |
|-----------|-------|
| security_reviewer | `scan_secrets`, `check_injection_patterns` |
| style_reviewer | `lint_style_conventions` |
| logic_reviewer | `analyze_control_flow` |
