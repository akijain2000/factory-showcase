# Wave 1: System Prompts — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 2 (System Prompt Quality)  
**Baseline:** Mean ~6.5/10 on this dimension (prompts were 44-69 lines, missing key sections)

## What was done

Enriched all 20 system-prompt.md files with:
- Version header updated to v2.0.0 with changelog
- Refusal and escalation paths (when to refuse, when to escalate to human)
- Memory strategy (ephemeral vs durable, retention policy)
- Abstain rules (when NOT to call tools)
- Structured output format (final answer shape)
- Cost awareness section (agents 11-20 were missing this)
- Latency section (agents 11-20 were missing this)

## What INCREASES score (learnings)

1. **Explicit refusal paths** — Without these, agents have no guardrails for out-of-scope or dangerous requests. Adding "never do X" + "escalate when Y" is the single biggest quality signal.
2. **Memory strategy** — Distinguishing ephemeral (session) from durable (persistent) prevents agents from hallucinating state they don't have.
3. **Abstain rules** — Telling the agent when NOT to use tools prevents unnecessary API calls and shows restraint/intelligence.
4. **Structured output** — Defining the answer shape (sections, fields) makes outputs predictable and parseable.
5. **Version + changelog** — Shows the prompt is a managed artifact, not a one-shot draft.
6. **Domain-specific constraints** — Generic prompts score lower. Each agent's refusal/escalation should reference its specific domain risks.

## What DECREASES score (anti-patterns found)

1. **Copy-paste sections** — If refusal/memory/abstain sections are identical across agents, graders detect it as "template slop" and penalize.
2. **Missing cost awareness** — Agents 11-20 had zero cost/latency guidance, which is a hard fail on CLASSic Cost dimension.
3. **Vague stop conditions** — "Stop when done" is not a stop condition. Must be specific and measurable.
4. **Tool name drift** — If system prompt mentions tools not in the tools/ directory (or vice versa), it's a consistency violation.
5. **No escalation path** — Agents that "try forever" without escalation are dangerous in production.

## Metrics after Wave 1

- Prompt lines: min 77, max 101 (was: min 44, max 69)
- All 20 agents: refusal=yes, memory=yes, abstain=yes, structured=yes
- Estimated dim 2 score: 8.0-8.5/10 (up from ~6.5)

## Remaining gap to 9/10

- Tool alignment verification (ensure every tool in prompt matches tools/ directory)
- Worked examples showing multi-turn conversation flow
- Agent self-monitoring instructions (when to check own output quality)
