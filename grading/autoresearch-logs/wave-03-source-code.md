# Wave 3: Source Code — Learning Log

**Date:** 2026-04-04  
**Target dimension:** AGENT_SPEC dim 1 (Source Code Quality)  
**Baseline:** Mean ~4.0/10 on this dimension (skeleton NotImplementedError stubs)

## What was done

Replaced all 20 skeleton agent.py files with real implementations:
- Full AgentState enum (IDLE, PLANNING, EXECUTING, WAITING_TOOL, ERROR, DONE)
- Explicit state machine with transition tables
- ReAct/Plan-Execute/Domain-specific loops per agent
- Circuit breakers: max_steps, max_wall_time_s, max_spend_usd
- Per-tool timeouts with ThreadPoolExecutor
- Retryable error handling (one retry on retryable errors)
- Structured logging with step_num, state, tool_name, elapsed_ms
- Persistence: save_state() and load_state() JSON round-trip
- Audit logs tracking all mutations for rollback

## What INCREASES score (learnings)

1. **State machine with explicit transitions** — The single biggest score driver. A state enum + transition table makes the agent's behavior provable and debuggable. Without it, agents are "vibes-based" and unpredictable.
2. **Circuit breakers** — max_steps prevents infinite loops, max_wall_time_s prevents runaway cost, max_spend_usd prevents budget blow-up. All three are essential for production agents.
3. **LLMClient as Protocol** — Using Protocol (structural subtyping) instead of ABC makes the agent testable with any mock. This is the right abstraction level.
4. **Domain-specific loop patterns** — Copy-paste loops score poorly. Each agent should implement its ACTUAL pattern:
   - File organizer: simple ReAct (think-act-observe)
   - DB admin: safety-gated (requires approval_id for DDL)
   - Workflow orchestrator: DAG topological execution
   - Security hardened: sanitize → detect → gate → validate pipeline
   - Parallel executor: fan-out/fan-in with trace aggregation
5. **Audit logs** — Tracking mutations enables rollback and forensic analysis. Without this, agents are untestable in production.
6. **Tool allowlists** — Restricting which tools an agent can call prevents prompt injection from accessing unauthorized capabilities.

## What DECREASES score (anti-patterns found)

1. **NotImplementedError stubs** — The #1 score killer. A skeleton that raises NotImplementedError gets 0/10 on source code. Even a minimal loop is vastly better.
2. **No state machine** — Without explicit states, agents can get stuck in undefined states. Common failure: tool returns error, agent re-enters the same tool call forever.
3. **No circuit breakers** — Without limits, a single bad prompt can consume the entire budget. This is the most common production failure mode.
4. **Generic loop for all agents** — Using the same ReAct loop for a security agent and a file organizer shows no domain understanding.
5. **No persistence** — Agents that can't checkpoint can't survive process restarts. This is a hard requirement for long-running agents.
6. **ThreadPoolExecutor limitation** — Python's thread-based timeout doesn't actually cancel the running tool. True cancellation requires process isolation or cooperative cancellation tokens. This is a known limitation to document.

## Metrics after Wave 3

- 20/20 agents: real implementations (no stubs)
- 20/20 compile with python3 -m py_compile
- Line counts: 171-200 (all under 200 cap)
- All agents have: state machine, circuit breakers, timeouts, persistence, audit logs
- Estimated dim 1 score: 8.5-9.0/10 (up from ~4.0)

## Remaining gap to 9/10

- Type hints could be stricter (some Any types remain)
- Error recovery could be more sophisticated (multi-retry with backoff)
- Some agents could benefit from async/await instead of threads
