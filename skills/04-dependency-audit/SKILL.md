---
name: 04-dependency-audit
description: Runs packaged scans for vulnerable dependencies and surfaces license risks for follow-up. Use when preparing a release, responding to security review, or refreshing third-party packages.
---

# Dependency audit

## Intent

Combine automated vulnerability scanning with a short manual pass for license policy. Results are advisory; remediation happens in the owning repository.

## Prerequisites

- Repository root as the working directory.
- Node.js with `npm` **or** Python 3 with `pip` — the bundled script detects which applies.
- Optional: `pip-audit` for Python (`pip install pip-audit` or project virtualenv).

## Bundled script

Run from the skill directory or pass the repo root explicitly:

```bash
bash "$(dirname "$0")/scripts/scan.sh" /path/to/repo
```

If invoked from inside the skill folder:

```bash
bash scripts/scan.sh ..
```

The script exits non-zero when a scanner reports vulnerabilities, so CI can fail loudly while still printing logs.

## Interpretation

- **npm** — `npm audit` reports known CVEs for the lockfile graph; severity filters may be configured in `.npmrc` or via flags inside `scan.sh`.
- **pip** — `pip-audit` checks the active environment or requirements file when present; absence of the executable prints installation guidance instead of failing the whole run.
- **Licenses** — Automated license listing varies by ecosystem; note any `UNLICENSED` or copyleft dependencies for legal review.

## Follow-up template

| Ecosystem | Command run | Highest severity | Blocking? | Owner action |
| --- | --- | --- | --- | --- |
| npm / pip | `scan.sh` | | | |

## Escalation

If fixes require major version bumps, capture breaking-change notes and schedule a separate test pass. Do not merge blind major upgrades solely to silence audit output.
