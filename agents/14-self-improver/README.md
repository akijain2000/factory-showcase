# Self-Improver Agent (Autoresearch Harness)

An agent that runs a **Karpathy-style loop** on its own instructions: **read** the current prompt, **hypothesize** improvements, **edit**, **evaluate** on fixed benchmarks, **compare** metrics, then **commit or revert** under governance.

## Audience

Research engineers and applied teams who want **controlled self-improvement** of system prompts with **reproducible evals** and **no silent production drift**.

## Quickstart

1. Load `system-prompt.md` (this file is the *outer* agent; the harness edits an **inner** prompt asset).
2. Point tools at your prompt registry and eval runner.
3. Use `src/agent.py` as the canonical loop ordering.

## Configuration

| Variable | Description |
|----------|-------------|
| `PROMPT_REGISTRY_URI` | Storage for prompt versions and diffs |
| `EVAL_SUITE_REF` | Benchmark suite manifest (tasks, graders) |
| `METRICS_STORE_URI` | Time-series or table for `compare_metrics` |
| `MODEL_API_ENDPOINT` | Model used for eval rollouts (secrets via host) |

## Architecture

```
 +------------------+
 | Karpathy loop    |
 +--------+---------+
          |
          v
 +------------------+       +------------------+
 | read_current_    |------>| edit_prompt      |
 | prompt           |       | (draft change)   |
 +------------------+       +--------+---------+
                                       |
                                       v
                             +------------------+
                             | run_evaluation   |
                             | (frozen suite)   |
                             +--------+---------+
                                       |
                                       v
                             +------------------+
                             | compare_metrics  |
                             | (baseline vs     |
                             |  candidate)      |
                             +--------+---------+
                                       |
                        +--------------+--------------+
                        |                             |
                        v                             v
               +----------------+            +----------------+
               | commit_or_     |            | commit_or_     |
               | revert KEEP    |            | revert DISCARD |
               +----------------+            +----------------+
```

## Governance

- **Frozen evals:** suite hash pinned per run.
- **Promotion:** human or automated gate on `compare_metrics`.
- **Rollback:** single command via `commit_or_revert`.

## Testing

See `tests/` for keep vs. discard decisions.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
