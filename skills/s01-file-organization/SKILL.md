---
name: s01-file-organization
description: Analyzes repository assets, classifies them, and applies repeatable folder layouts for repositories. Use when trees are cluttered, conventions are missing, or the file-organizer agent needs a shared playbook.
---

# File classification and organization

## Goal / overview

Establish a stable taxonomy for files (source, config, docs, generated, secrets-adjacent) and map each path into the correct bucket before moves or renames. The outcome is a predictable tree that pairs with agent `01-file-organizer`.

## When to use

- A repository mixes prototypes, shipped code, and scratch files at the root.
- New contributors cannot guess where to add modules, fixtures, or runbooks.
- An automated organizer needs rules that stay consistent across sessions.

## Steps

1. Inventory the top-level entries and tag each as **mutable source**, **build output**, **documentation**, **operational**, **third-party**, or **unknown**.
2. Define or adopt naming rules (prefixes, `src/` vs `lib/`, `docs/` vs `design/`) and write them as a short table: pattern → intended location.
3. Flag paths that must not move without review: credential templates, deployment manifests, generated lockfiles, and vendor snapshots.
4. Propose a target tree; group by domain (feature or bounded context) when the codebase is large, otherwise by layer (`api`, `services`, `cli`).
5. Order moves in dependency-safe sequence: shared utilities first, then dependents; avoid breaking import paths without an explicit rename plan.
6. After each batch of moves, verify build, test, and doc links still resolve (or list follow-up edits).

## Output format

- **Classification table**: path (or glob), current role, target folder, risk (low/medium/high).
- **Move plan**: ordered steps with rationale per step.
- **Verification checklist**: commands or link checks to run after reorganization.

## Gotchas

- Moving files without updating imports, CI paths, or README links creates silent breakage.
- Treat `.env` and key material as immovable; only document expected placement.
- Generated folders should stay out of hand-edited trees or be clearly marked to prevent merge noise.

## Test scenarios

1. **Messy monorepo root**: Given ten mixed folders at repo root, produce a classification table and ordered move plan with zero moves into generated-output directories.
2. **Breaking import risk**: Given a Python package where `tests/` import from `src/` via relative paths, list moves that preserve import graph and call out any required `__init__.py` updates.
3. **Secrets adjacent**: Given a tree containing `.env.example` and `docker-compose.yml`, classify everything, mark high-risk paths, and output a plan that leaves credential templates in place while cleaning non-secret clutter.
