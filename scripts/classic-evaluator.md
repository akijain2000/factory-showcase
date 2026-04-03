# CLASSic Framework Evaluator

Supplementary evaluation template for AI agent projects. Grades each agent on 5 production-readiness dimensions that complement the 8 AGENT_SPEC dimensions.

Based on the CLASSic framework (2026) from enterprise agent evaluation research.

## Dimensions (0-10 each)

### Cost (C)

Does the agent manage computational expense?

| Score | Anchor |
|-------|--------|
| 0-2 | No mention of tokens, budgets, or model costs |
| 3-4 | Acknowledges cost exists but no controls |
| 5-6 | Tracks token usage; has some budget awareness |
| 7-8 | Model routing by task complexity; budget circuit breakers; cost reporting |
| 9-10 | Full cost optimization: tiered models, token caching, budget allocation per step, cost-per-outcome tracking |

Signals to look for in agent files:
- `system-prompt.md`: mentions tokens, budget, cost, model tiers
- `tools/`: cost estimation tools, budget-check tools
- `src/`: token counting, model routing logic
- `tests/`: budget exhaustion scenarios

### Latency (L)

Does the agent optimize for response time?

| Score | Anchor |
|-------|--------|
| 0-2 | Sequential everything, no timeout design |
| 3-4 | Basic timeouts on tool calls |
| 5-6 | Some parallel execution or caching |
| 7-8 | Streaming responses; parallel tool calls; result caching; timeout hierarchies |
| 9-10 | Full latency optimization: speculative execution, warm caches, progressive rendering, P99 targets |

Signals:
- Streaming architecture, parallel tool calls
- Timeout configuration in deploy/
- Caching strategies in system prompt or tools
- Response time monitoring

### Accuracy (A)

Does the agent verify its own outputs?

| Score | Anchor |
|-------|--------|
| 0-2 | No output validation |
| 3-4 | Basic format checking |
| 5-6 | Self-verification on critical outputs |
| 7-8 | Confidence scoring; output validation tools; re-try on low confidence |
| 9-10 | Full verification: multi-pass checking, ground-truth comparison, calibrated confidence, hallucination detection |

Signals:
- Output validation in system prompt constraints
- Self-check steps in workflow
- Confidence thresholds
- Verification tools

### Stability (S1)

Does the agent produce consistent results?

| Score | Anchor |
|-------|--------|
| 0-2 | No retry logic, crashes on unexpected input |
| 3-4 | Basic error handling |
| 5-6 | Retry with backoff; graceful degradation on some failures |
| 7-8 | Structured error recovery; fallback behaviors; consistent output schema |
| 9-10 | Full stability: idempotent operations, deterministic fallbacks, chaos-tested, regression suite |

Signals:
- Error handling in system prompt
- Retry logic in src/
- Fallback behaviors defined
- Graceful degradation patterns

### Security (S2)

Does the agent defend against misuse?

| Score | Anchor |
|-------|--------|
| 0-2 | No security consideration |
| 3-4 | Basic input validation |
| 5-6 | Input sanitization; some access controls |
| 7-8 | Injection detection; output filtering; least privilege; audit logging |
| 9-10 | Full defense-in-depth: trust zones, input/output sanitization, injection detection, permission matrix, PII redaction, audit trail |

Signals:
- Security constraints in system prompt
- Sanitization/validation tools
- Least privilege in deploy config
- Audit logging

## Scoring Procedure

1. Read README.md, system-prompt.md, all tools/, src/, tests/, deploy/
2. For each CLASSic dimension, identify which signals are present
3. Score 0-10 using the anchors above
4. Record evidence (which file, which section)
5. Overall CLASSic score = mean of 5 dimensions

## Interpretation

| Overall | Assessment |
|---------|------------|
| 0-3 | Not production-ready on operational dimensions |
| 4-5 | Minimal awareness, significant gaps |
| 6-7 | Adequate for internal/staging use |
| 8-9 | Production-ready with operational maturity |
| 10 | Best-in-class operational engineering |
