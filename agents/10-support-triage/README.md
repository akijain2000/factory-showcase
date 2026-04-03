# Support Triage Agent

**Pattern:** Routing + classification  
**Goal:** Classify ticket intent, retrieve knowledge-base evidence, route to the correct queue or specialist agent, draft a first response, and escalate when confidence or policy demands human judgment.

## Architecture

Inbound tickets pass through a **classification** stage producing **structured output** (JSON). **Routing rules** map labels + severity + account tier to destinations. Retrieval and response generation are separate **tool** stages to keep audit trails clean.

```
      +-----------+
      |  Ticket   |
      +-----+-----+
            |
     +------v------+
     |classify_intent|
     +------+------+
            |
    +-------+-------+
    | structured    |
    | labels + conf |
    +-------+-------+
            |
 +----------+----------+
 |                       |
 v                       v
+----------+      +-------v------+
| search_kb|      | route_ticket |
+----------+      +-------+------+
                          |
              +-----------+-----------+
              |                       |
       +------v------+         +------v------+
       |generate_    |         |escalate_to_ |
       |response     |         |human        |
       +-------------+         +-------------+
```

**Structured output contract:** Classification JSON **must** include: `primary_intent`, `secondary_intents`, `urgency`, `sentiment`, `confidence` (0–1), `entities`, `routing_hint`.

## Contents

| Path | Purpose |
|------|---------|
| `system-prompt.md` | Classification schema + routing **rules** |
| `tools/` | Triage tool specs |
| `tests/` | Routing behavior |
| `src/` | Orchestration skeleton |

## Governance

Log every `route_ticket` decision with ticket id and model version for compliance review.
