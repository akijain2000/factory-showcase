# Learning Tutor Agent

**Pattern:** Memory-heavy personalized tutoring  
**Goal:** Track learner progress, adapt difficulty, and retain both factual knowledge (semantic) and session-specific facts (episodic) across interactions.

## Architecture

The tutor separates **semantic memory** (stable concepts, curriculum mappings, skill graphs) from **episodic memory** (per-session events, mistakes, emotional cues, timestamps). Tool calls write to and read from these layers; the model prompt encodes when to use each.

```
                    +------------------+
                    |   User / LMS     |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Tutor Runtime   |
                    |  (orchestration) |
                    +--------+---------+
           +---------+--------+---------+---------+
           |                  |                   |
    +------v------+   +-------v-------+   +-------v-------+
    | assess_     |   | generate_     |   | store_        |
    | knowledge   |   | exercise      |   | progress      |
    +------+------+   +-------+-------+   +-------+-------+
           |                  |                   |
           +------------------+-------------------+
                              |
              +---------------v---------------+
              |      recall_history (read)     |
              +---------------+---------------+
                              |
         +--------------------+--------------------+
         |                                         |
  +------v------+                         +--------v--------+
  |  Semantic   |                         |   Episodic      |
  |  store      |                         |   store         |
  | (skills,    |                         | (sessions,      |
  |  rubrics)   |                         |  attempts)      |
  +-------------+                         +-----------------+
```

**Data flow:** `assess_knowledge` and `recall_history` inform the next turn; `generate_exercise` consumes difficulty tags from both memory layers; `store_progress` appends episodic events and updates semantic aggregates (e.g., mastery scores).

## Contents

| Path | Purpose |
|------|---------|
| `system-prompt.md` | Persona, memory rules, tool-use policy |
| `tools/` | JSON-oriented specs per tool |
| `tests/` | Behavioral scenarios |
| `src/` | Skeleton runtime wiring |

## Operational notes

- Persist episodic records with stable `learner_id` and monotonic `sequence` or timestamps.
- Refresh semantic summaries on a schedule or after N new episodic writes to avoid drift.
