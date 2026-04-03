# Eval Agent (Adaptive Rubrics)

An **evaluation specialist** that synthesizes **task-specific rubrics**, scores multi-step trajectories, filters evidence by rubric dimensions, and **calibrates** scoring to reduce drift across models and prompts (AdaRubric-style workflow).

## Audience

ML platform teams and product engineers who need **repeatable quality gates** for agent traces, RAG answers, or tool-using runs—without hand-writing a new rubric for every task variant.

## Quickstart

1. Load `system-prompt.md`.
2. Mount tools under `tools/` with strict JSON schema validation.
3. Point `MODEL_API_ENDPOINT` at your evaluator model (may differ from the producer model).
4. Validate with `tests/rubric-calibration-filter-flow.md`.

## Configuration

| Variable | Description |
|----------|-------------|
| `EVAL_AGENT_MODEL_ENDPOINT` | Scoring model endpoint (alias allowed) |
| `EVAL_AGENT_RUBRIC_REGISTRY_REF` | Storage for versioned rubrics |
| `MODEL_API_ENDPOINT` | Fallback general model for rubric generation |

## Architecture

```
 +----------------+     +----------------------+
 | Task description|---->| Rubric generation    |
 +----------------+     | (criteria + weights) |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        | Trajectory scoring   |
                        | (per-step + global)  |
                        +----------+-----------+
                                   |
           +------------------------+------------------------+
           |                        |                        |
           v                        v                        v
 +------------------+    +------------------+    +------------------+
 | Dimension filter |    | Score aggregation|    | Calibration pass |
 | (keep/drop ev.)  |    | (weighted mean)  |    | (anchor examples)|
 +------------------+    +------------------+    +------------------+
           \------------------------+------------------------/
                                    |
                                    v
                         +----------------------+
                         | Calibrated output    |
                         | (scores + rationale) |
                         +----------------------+
```

## Quality posture

- Rubrics are **versioned** and **frozen** before bulk scoring.
- Calibration uses **anchor trajectories** with adjudicated labels when available.
- Dimension filters prevent **overfitting** to verbose but irrelevant model chatter.

## Testing

See `tests/rubric-calibration-filter-flow.md`.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
