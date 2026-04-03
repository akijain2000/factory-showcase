# Improvements: Findings and Changes

Based on grading 10 skills and 10 agents against their respective quality specs, the following systematic weaknesses were identified and fixes applied to both factory repositories.

## Key Findings

### Skill Factory

| Finding | Severity | Evidence |
|---------|----------|----------|
| No test scenario validation | High | 9/10 skills lack the SKILL_SPEC-required ">=3 test scenarios". Validator did not catch this. |
| Evaluation is consistently weakest dimension | Medium | All good skills scored 7/10 on Evaluation — lowest of all dimensions. |
| Validator passes skills with no examples | Low | SKILL_SPEC recommends examples but validator does not check for them. |

### Agent Factory

| Finding | Severity | Evidence |
|---------|----------|----------|
| No `src/` directory validation | High | AGENT_SPEC canonical structure requires `src/` but validator did not check. |
| No `deploy/` directory validation | High | Same gap for `deploy/` directory. |
| Testing dimension consistently weak (mean 6.4) | Medium | All agents have exactly 1 behavioral test — minimum spec compliance only. |
| Observability dimension weakest (mean 6.1) | Medium | Only 2/10 agents have explicit tracing/logging design. |
| Memory design underexplored (mean 6.4) | Medium | Only 2/10 agents have thoughtful memory architectures. |
| Secret pattern regex too broad | Low | `OPENAI` in env var names (e.g., `MODEL_API_KEY` docs) triggered false positives initially. |

## Changes Applied

### Skill Factory: `scripts/validate-skill.ts`

**Added test scenario check:** The validator now warns when SKILL.md body lacks a test/evaluation/scenarios/verify section, pointing to the SKILL_SPEC requirement for >=3 test scenarios.

```typescript
// Test scenarios check (SKILL_SPEC requires >=3 real test scenarios)
const hasTestSection = /#{1,3}\s*(test|evaluation|scenarios|verify)/i.test(body);
if (!hasTestSection) {
  issues.push({ severity: "warning", message: "No test/evaluation section found..." });
}
```

### Agent Factory: `scripts/validate-agent.ts`

**Added `src/` directory check:** Warns when the canonical `src/` directory is missing or empty.

**Added `deploy/` directory check:** Warns when the canonical `deploy/` directory is missing.

**Both checks are warnings (not errors)** since some agent projects may use alternative layouts while still meeting spec intent.

```typescript
const srcN = srcExists ? fs.readdirSync(srcPath).filter(...).length : 0;
out("Source directory", srcN > 0 ? "Pass" : "Warn", ...);

const deployExists = exists(deployPath) && fs.statSync(deployPath).isDirectory();
out("Deploy directory", deployExists ? "Pass" : "Warn", ...);
```

## Research-Backed Recommendations (Not Yet Implemented)

From web research on 2026 best practices:

1. **CLASSic Framework** (Cost, Latency, Accuracy, Stability, Security): Could complement the existing 8 AGENT_SPEC dimensions for production evaluation. Source: Zylos Research 2026 agent evaluation guide.

2. **AdaRubric pattern** (task-adaptive evaluation): Rather than fixed grading dimensions, generate task-specific rubrics. Source: arxiv.org/abs/2603.21362.

3. **Parallel reasoning traces**: 2026 agent patterns support parallel tool execution with trace aggregation. Could be added to course Module 07 (Planning and Reasoning).

4. **Docker Agent / CUGA patterns**: Production multi-agent systems using declarative YAML configs. Could inform Agent Factory's multi-agent course modules.

## Quantitative Impact

| Metric | Before | After |
|--------|--------|-------|
| Skill validator checks | 12 | 13 (+test scenario warning) |
| Agent validator checks | 6 | 8 (+src, +deploy warnings) |
| Skills passing all checks (excl. #10) | 9/9 | 9/9 (new warning is additive) |
| Agents passing all checks | 10/10 | 10/10 (new warnings are additive) |
