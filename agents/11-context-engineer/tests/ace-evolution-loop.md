# Test: ACE evolution loop with quality gate and dry-run prompt

## Scenario

A long support session produced 200 log lines and three ticket comments. The agent must prepare context for a root-cause summary, reflect on a prior wrong answer, compress when near token limits, and propose a system prompt tweak **without** promoting it.

## Given

- `raw_artifacts` contains duplicate stack traces, one authoritative error block tagged as immutable, and noisy success polling lines.
- `CONTEXT_MAX_TOKENS` is set such that the curated bundle estimates 95% of limit after curation.
- Prior turn’s `model_output` violated success criteria by asserting a fix without reproduction steps.
- Runtime policy requires `evaluate_context_quality.pass === true` before `update_system_prompt` with `dry_run: false`; test uses dry-run path only.

## When

1. The agent invokes `curate_context` with a clear `objective` and `max_items`.
2. The agent invokes `evaluate_context_quality` on the resulting `bundle_id`.
3. The agent invokes `reflect_on_output` with populated `model_output` and success criteria.
4. The agent invokes `compress_context` targeting 70% of max tokens.
5. The agent invokes `update_system_prompt` with `dry_run: true` adding a bullet under tool-use: “Never claim verified fix without repro.”

## Then

- Curated bundle retains the immutable error block verbatim; duplicate traces collapse to a single ranked item with merged `source_ref` list in metadata (implementation-defined) or explicit drop reasons.
- `evaluate_context_quality` returns `pass: true` after compression or reports `gaps` that the agent addresses by re-curating—**not** by skipping the tool.
- `reflect_on_output` yields at least one `insights` entry with `category` related to **ungrounded_claim** or **missing_evidence**.
- `update_system_prompt` returns `dry_run: true`, `validation.safety_constraints_preserved: true`, and **no** live prompt version change in the host registry.
