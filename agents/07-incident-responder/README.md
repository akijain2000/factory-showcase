# Incident Responder Agent

**Pattern:** Autonomous monitoring loop with bounded autonomy  
**Goal:** Detect unhealthy signals, run safe diagnostics, open incidents, and escalate to humans when thresholds or step limits are hit.

## Architecture

The responder runs a **sense → diagnose → act → record** loop. **Circuit breakers** halt automated remediation when blast radius is unclear or repeated actions fail. **Escalation** triggers when severity, customer impact, or autonomy budget is exceeded.

```
  +-------------+     +-------------+     +---------------+
  | check_health|---->| query_logs  |---->| run_diagnostic|
  +------+------+     +------+------+     +-------+-------+
         |                    |                    |
         |           +--------v---------+          |
         |           |  Policy engine   |          |
         |           | (thresholds +    |          |
         |           |  max auton.      |          |
         |           |  steps)          |          |
         |           +--------+---------+          |
         |                    |                      |
         v                    v                      v
  +-------------+     +-------------+     +---------------+
  | (loop or    |     |notify_oncall|     |create_incident|
  |  handoff)   |     |  (optional) |     |  (ticket)     |
  +-------------+     +-------------+     +---------------+
```

**Bounded autonomy:** Each incident run carries a `max_autonomous_steps` counter; when exhausted, the agent **must** stop mutating state and **notify_oncall** with a structured handoff summary.

## Contents

| Path | Purpose |
|------|---------|
| `system-prompt.md` | Circuit breakers, thresholds, step budget |
| `tools/` | Health, logs, diagnostics, comms, ticketing |
| `tests/` | Escalation behavior |
| `src/` | Loop skeleton |

## Safety

- Default-deny destructive remediation unless explicitly in allowlist for the environment.
- All automated actions must be idempotent where possible and fully logged.
