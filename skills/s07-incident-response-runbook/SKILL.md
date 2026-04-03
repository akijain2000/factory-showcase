---
name: s07-incident-response-runbook
description: Structures bounded monitoring, diagnosis, and escalation during outages. Use when alerts fire, error budgets burn, or agent 07-incident-responder is engaged for live systems.
---

# Incident response with bounded autonomy

## Goal / overview

Defines a tight loop for operators and agents: confirm impact, narrow cause, take safe mitigations, and escalate before guesswork spreads. Autonomy stops at defined boundaries (no silent prod config edits without approval). Pairs with agent `07-incident-responder`.

## When to use

- Customer-facing error rate or latency crosses a threshold.
- A deploy, flag change, or dependency shift coincides with new failures.
- On-call needs a single timeline and owner list for a bridge call.

## Steps

1. **Triage signal**: record alert name, start time (UTC), scope (region, shard, single tenant), and user-visible symptoms.
2. **Severity**: map to org scale (e.g. SEV1 full outage vs SEV4 minor); set communication expectations (status page, internal only).
3. **Hypothesis queue**: list top three plausible causes ordered by evidence (deploy diff, dependency health, saturation, recent config).
4. **Bounded actions**: allow read-only inspection, metric pulls, log sampling, traffic shift or rollback *if* pre-authorized in the runbook; anything outside the list requires human sign-off.
5. **Mitigation first**: restore service with the smallest reversible change (rollback, scale, circuit break, disable feature flag); defer root-cause proof when users are still impacted.
6. **Escalation**: when time-box (e.g. 15 minutes) expires without relief, or blast radius grows, page the next tier with a one-page summary: impact, actions taken, current theory, what is needed.

## Output format

- **Incident header**: id, severity, commander, start time, status (investigating/mitigating/monitoring/resolved).
- **Timeline**: bullet log of events and decisions with timestamps.
- **Customer/comms**: short external text and longer internal technical note.
- **Post-incident hook**: list data to preserve for later review (graphs, deploy ids, config snapshots).

## Gotchas

- Correlation is not causation; a deploy during an incident is suspicious but not proof until metrics or rollback tests support it.
- Restart storms can worsen outages; cap concurrency on remediations that touch shared infrastructure.
- Partial recovery can hide failing replicas; verify all zones or cells before closing.

## Test scenarios

1. **Deploy correlation**: Error spike begins within five minutes of a release; runbook should propose rollback as first bounded test and measure before deeper debugging.
2. **Forbidden action**: Agent suggests editing a prod firewall rule not in the allowed list; flow should stop and request human approval without applying.
3. **Escalation timer**: No mitigation after the time-box; output should trigger escalation template with filled impact summary and empty-handed theories ruled out.
