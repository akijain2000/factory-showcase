#!/usr/bin/env bash
# Dependency vulnerability scan for Node (npm) and Python (pip-audit).
# Usage: scan.sh [REPO_ROOT]
# Exit codes: 0 = no issues reported, 1 = vulnerability found or fatal error, 2 = invalid usage

set -u

REPO_ROOT="${1:-.}"
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)" || {
  echo "scan.sh: cannot cd to repo root: $1" >&2
  exit 2
}

npm_exit=0
pip_exit=0
ran_any=0

log() {
  printf '%s\n' "$*"
}

run_npm_audit() {
  if [[ -f "$REPO_ROOT/package.json" ]]; then
    ran_any=1
    log "==> npm audit (repo: $REPO_ROOT)"
    if ! command -v npm >/dev/null 2>&1; then
      log "ERROR: package.json present but npm not found in PATH."
      return 1
    fi
    (cd "$REPO_ROOT" && npm audit --audit-level=moderate) || return 1
  fi
  return 0
}

run_pip_audit() {
  local req=""
  for candidate in "$REPO_ROOT/requirements.txt" "$REPO_ROOT/requirements-dev.txt"; do
    if [[ -f "$candidate" ]]; then
      req="$candidate"
      break
    fi
  done

  if [[ -f "$REPO_ROOT/pyproject.toml" || -n "$req" ]]; then
    ran_any=1
    log "==> pip-audit (repo: $REPO_ROOT)"
    if ! command -v pip-audit >/dev/null 2>&1; then
      log "WARNING: pip-audit not installed. Install with: python3 -m pip install pip-audit"
      log "Skipping Python audit."
      return 0
    fi
    if [[ -n "$req" ]]; then
      pip-audit -r "$req" || return 1
    elif [[ -f "$REPO_ROOT/pyproject.toml" ]]; then
      log "NOTE: pyproject.toml present without requirements*.txt; auditing the active Python environment (install project deps into the current venv first)."
      (cd "$REPO_ROOT" && pip-audit) || return 1
    fi
  fi
  return 0
}

if ! run_npm_audit; then
  npm_exit=1
fi

if ! run_pip_audit; then
  pip_exit=1
fi

if [[ "$ran_any" -eq 0 ]]; then
  log "No package.json, pyproject.toml, or requirements*.txt found at $REPO_ROOT — nothing to scan."
  exit 0
fi

if [[ "$npm_exit" -ne 0 || "$pip_exit" -ne 0 ]]; then
  log "scan.sh: completed with vulnerabilities or errors (npm=$npm_exit pip=$pip_exit)."
  exit 1
fi

log "scan.sh: no moderate+ npm issues reported; pip-audit clean or skipped."
exit 0
