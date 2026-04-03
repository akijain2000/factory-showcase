---
name: s15-agent-to-agent-delegation
description: Finds peer agent capabilities, negotiates handoffs, and delegates subtasks across agents. Use when work spans specialized agents, trust boundaries differ, or agent 15-a2a-coordinator routes requests.
---

# Agent-to-agent delegation and handoffs

## Goal / overview

Split work so each agent stays inside its competence and authority: discover what another agent can do, agree on inputs and outputs, and delegate without losing accountability. Pairs with agent `15-a2a-coordinator`.

## When to use

- A task needs domain skills (e.g. security review plus implementation) that live in separate agents.
- Multiple automations could duplicate work or fight over shared resources.
- Upstream agents must not assume downstream tools or data the peer cannot access.

## Steps

1. **Capability discovery**: query or read manifest for each candidate peer—supported intents, required auth, rate limits, output schemas.
2. **Task decomposition**: break the parent goal into subtasks with clear inputs, acceptance checks, and dependencies (DAG or ordered list).
3. **Match subtasks to peers**: assign by capability fit; if two peers qualify, prefer the one with tighter scope and lower privilege.
4. **Protocol negotiation**: agree on message format (versioned payload, idempotency key, timeout, reply channel); reject or upgrade version on mismatch.
5. **Delegate**: send bounded context—minimal data needed, no excess secrets; include correlation id for tracing across agents.
6. **Aggregate and verify**: merge peer results; run cross-checks (lint, policy, human gate) before treating the combined output as final.

## Output format

- **Delegation graph**: nodes (agents), edges (subtasks), data passed on each edge.
- **Handshake log**: capability versions agreed, timeouts, retry policy.
- **Result bundle**: per-peer response summary, merged artifact, open gaps.

## Gotchas

- Passing credentials between agents widens blast radius; prefer scoped tokens or proxy calls through a single gatekeeper.
- Without idempotency, retries can double-charge or double-apply side effects.
- Circular delegation (A asks B asks A) needs a depth limit and cycle detection.

## Test scenarios

1. **Version skew**: Peer advertises schema v2; coordinator speaks v1; negotiation should fail closed or upgrade explicitly before work starts.
2. **Least privilege**: A research task and a deployment task are both available; coordinator should route deploy steps only to the peer with deploy rights.
3. **Partial failure**: Two peers run in parallel; one times out; output should show completed partial results, mark the timeout, and define retry or fallback without silent success.
