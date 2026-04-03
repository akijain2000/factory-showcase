---
name: s13-cost-aware-model-routing
description: Routes tasks across models using budgets, token estimates, and spend limits. Use when API bills climb, workloads mix trivial and hard prompts, or agent 13-cost-optimizer tunes inference.
---

# Cost-aware model routing and spend guards

## Goal / overview

Match model capability to task difficulty while keeping monthly and per-request spend inside defined rails. Covers rough token estimation, tiered routing, and circuit breakers when budgets exhaust. Pairs with agent `13-cost-optimizer`.

## When to use

- Traffic includes high-volume classification next to rare, deep reasoning calls.
- Finance or product sets a hard cap on inference spend per environment or customer.
- Latency SLAs still matter—cheapest is not always acceptable.

## Steps

1. **Task classes**: label incoming work (e.g. extract, classify, summarize long doc, codegen, multi-step agent). Map each class to a default model tier.
2. **Token estimate**: count or approximate input length (chars/4 heuristic with calibration for the tokenizer when available); add expected output budget per class.
3. **Price table**: maintain per-model rates (input/output per 1k tokens or per image minute) in one place; refresh when providers change lists.
4. **Routing rules**: if estimated cost under threshold A use economy model; if confidence low or self-check fails, escalate tier once; cap escalations per request.
5. **Circuit breakers**: daily or monthly budget counters; on breach, switch to cheaper tier, queue, or fail closed with a user-visible degradation per policy.
6. **Observability**: log model id, estimated vs billed tokens when available, task class, and customer or tenant id for chargeback.

## Output format

- **Routing matrix**: task class → default model → escalation model → max escalations.
- **Budget config**: limits (per day, per tenant, burst), breaker actions, reset windows.
- **Runbook snippet**: what operators see when a breaker trips and how to re-enable safely.

## Gotchas

- Cached or deduplicated inputs change unit economics; routing logic should not assume every call is full price.
- Long tool loops multiply tokens fast; budget guards belong on the outer agent loop, not only the first LLM call.
- Degrading quality without telling downstream callers can break contracts—surface degradation flags in API responses when required.

## Test scenarios

1. **Simple majority**: Ten thousand short classifications in a day; routing should keep them on the economy tier and stay under a stated daily cap.
2. **Escalation cap**: Hard task retries three times with tier bumps; fourth attempt should stop escalation and return partial result or error per policy.
3. **Breaker trip**: Monthly spend crosses limit mid-day; system should flip to cheapest tier or block and emit an alert without silent overage.
