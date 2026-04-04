# Wave 4: Testing — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 6 (Testing Quality)  
**Baseline:** Mean ~5.0/10 on this dimension (1 test per agent, happy path only)

## What was done

Expanded test suites from 1 to 4 files per agent (80 total test files):
- test-error-recovery.md: tool failures, retries, timeouts, circuit breaker triggers
- test-adversarial.md: prompt injection, malformed input, privilege escalation, data exfiltration
- test-regression.md: domain-specific edge cases unique to each agent

## What INCREASES score (learnings)

1. **Error recovery tests** — The highest-value addition. Production agents fail on tool errors 10-30% of the time. Testing retry logic, circuit breakers, and graceful degradation is essential.
2. **Adversarial tests** — Prompt injection is the #1 security risk for LLM agents. Every agent needs at least 3 injection scenarios: ignore-instructions, fake-tool-output, privilege-escalation.
3. **Domain-specific regression** — Generic tests don't catch domain edge cases. A knowledge graph agent needs entity resolution conflict tests. A DB admin agent needs concurrent DDL tests. These are different problems requiring different test designs.
4. **Structured test format** — Using Scenario/Setup/Steps/Expected/Pass criteria makes tests reproducible and auditable. Free-form test descriptions lose context.
5. **Tool mock alignment** — Test mocks must use the EXACT error codes from the tool's error taxonomy. Using made-up error codes shows the test author didn't read the tool spec.
6. **Multiple failure modes per test** — A single "tool fails" test is weak. Testing retryable → success, fatal → stop, timeout → report, and cascade → circuit breaker covers the real failure space.

## What DECREASES score (anti-patterns found)

1. **Happy path only** — Having only 1 test that shows the agent working correctly tells you nothing about failure behavior. This was the baseline state for all 20 agents.
2. **No adversarial testing** — Without injection tests, there's no evidence the agent's constraints actually work.
3. **Generic error tests** — "Tool returns error, agent handles it" is too vague. The test must specify WHICH error code, WHETHER it's retryable, and WHAT the agent should do differently.
4. **Missing setup/mock details** — Tests without explicit tool mocks can't be reproduced. "Agent handles failures" is a wish, not a test.
5. **No circuit breaker tests** — Testing individual failures is good, but testing cascading failures that trigger circuit breakers is what separates production-grade from toy agents.

## Metrics after Wave 4

- 80 test files total (20 agents x 4 tests each)
- Coverage: happy path + error recovery + adversarial + regression
- All tests follow structured format (Scenario/Setup/Steps/Expected/Pass)
- Estimated dim 6 score: 8.5-9.0/10 (up from ~5.0)

## Remaining gap to 9/10

- Could add a 5th test: performance/load test (many concurrent requests)
- Could add property-based test descriptions (invariants that always hold)
- Could automate test execution with a test runner harness
