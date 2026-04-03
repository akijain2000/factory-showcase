---
name: 07-test-coverage-analyzer
description: Analyzes test coverage gaps in a codebase by mapping source modules to their corresponding test files and identifying untested functions, branches, and edge cases. Use when reviewing test completeness, preparing for a release, or auditing a new codebase for testing gaps.
---

# Test Coverage Analyzer

Identify what is tested, what is not, and where new tests would have the highest impact.

## Procedure

1. **Discover project structure.** List source directories and test directories. Identify the testing framework from config files (package.json, pyproject.toml, Cargo.toml, build.gradle, etc.) or from test file naming conventions.

2. **Map source to tests.** For each source file, find corresponding test files by naming convention (e.g., `foo.ts` → `foo.test.ts`, `bar.py` → `test_bar.py`) and by import analysis (which test files import which source modules).

3. **Identify coverage gaps.** Flag source files with:
   - No corresponding test file at all.
   - Test file exists but covers fewer than half the exported functions/classes.
   - Complex logic (nested conditionals, error handling, state transitions) without branch-level tests.

4. **Prioritize gaps.** Rank untested code by risk:
   - Public API surfaces and entry points (highest).
   - Error handling and edge-case paths.
   - Business logic with side effects (database writes, external calls).
   - Internal utilities and pure functions (lowest unless widely used).

5. **Produce the report** using the output template below.

## Output template

```markdown
## Test Coverage Analysis

### Summary
- Source files: N
- Test files: M
- Files with no test coverage: X
- Estimated function-level coverage: ~Y%

### Critical gaps (recommend immediate tests)
| Source file | Risk | Reason |
|-------------|------|--------|
| ... | High | Public API, no tests |

### Moderate gaps
| Source file | Risk | Reason |
|-------------|------|--------|
| ... | Medium | Error paths untested |

### Well-covered modules
- ...

### Recommended next tests
1. ...
2. ...
3. ...
```

## Validation loop

After producing the report:
1. Verify each "no test" claim by searching for the source file name across all test directories.
2. Check that "well-covered" modules actually have assertions, not just imports.
3. Re-rank if new evidence changes risk assessment.

## Portability notes

This skill works with any language and test framework. Do not assume specific CLI commands are available. Rely on file system inspection (directory listings, file reads, import/require analysis) rather than running coverage tools. If the project has a coverage config or CI badge, note the reported number but still perform independent file-level analysis.
