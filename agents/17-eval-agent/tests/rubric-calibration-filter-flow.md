# Test: rubric generation, scoring, dimension filter, calibration, aggregation

## Scenario

For a customer-support summarization task, the agent generates a rubric, scores several trajectories, filters noisy spans for one trajectory, calibrates weights using anchor labels, and aggregates cohort scores against a gate.

## Given

- A task spec with three success criteria and two explicit negative examples.
- Five stored trajectories `tr_a` … `tr_e` with known human labels on `tr_a`, `tr_b`, `tr_c`, `tr_d`, `tr_e` for calibration.
- `tr_c` contains long boilerplate turns that should be filtered before rescoring.

## When

- The agent calls `generate_rubric` with three dimensions (correctness, citation compliance, brevity) whose weights sum to `1.0`.
- The agent calls `score_trajectory` for each trajectory using `granularity: final`.
- The agent calls `filter_by_dimension` on `tr_c` with `keep_top_k_per_dimension` and `top_k: 4`.
- The agent rescores `tr_c` using `filtered_ref` returned from the filter step (integrator passes substituted ref).
- The agent calls `calibrate_rubric` with anchors from all five labeled trajectories and `objective: maximize_spearman`.
- The agent calls `aggregate_scores` with `method: trimmed_mean`, `trim_percent: 0.1`, and a gate requiring `citation_compliance >= 0.8` mean.

## Then

- `generate_rubric` returns `validation.ok: true` and a stable `rubric_id`.
- Post-filter scoring for `tr_c` shows **higher** `brevity` than pre-filter scoring in the harness fixtures.
- `calibrated_rubric_id` differs from `base_rubric_id` and includes a monotonically increasing `revision`.
- `aggregate_scores` references the **calibrated** rubric id used for final scoring passes.
- Gate results match harness expectations (pass or fail) with explicit `failed_reasons` when failing.
