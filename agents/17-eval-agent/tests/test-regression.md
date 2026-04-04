# Test: empty trajectory, rubric dimension mismatch, calibration overflow

## Scenario

Regression cases: (1) scoring an empty trajectory (zero turns); (2) scoring with a rubric whose dimensions do not match filter/score expectations; (3) calibration produces non-finite or out-of-range weights (overflow / numerical blow-up) that must be clamped or rejected.

## Setup

- Agent config: `EVAL_AGENT_RUBRIC_REGISTRY_REF=registry://eval/reg`, default gate requires dimensions `correctness`, `citation_compliance`, `brevity`.
- Tools mocked:
  - `generate_rubric` → can return rubric `rub_dim2` with only two dimensions for case (2).
  - `score_trajectory` → for empty trajectory ref `tr_empty`: `{ "ok": false, "error": "EMPTY_TRAJECTORY" }` or `{ "ok": true, "scores": {}, "warning": "empty" }` per harness contract being tested.
  - `filter_by_dimension` → when rubric lacks requested dimension: `{ "ok": false, "error": "DIMENSION_MISMATCH", "missing": ["brevity"] }`.
  - `calibrate_rubric` → returns weights summing to `1.0` but one weight `1e308` or `NaN` variant per harness case (3), triggering `{ "ok": false, "error": "CALIBRATION_NUMERIC_OVERFLOW" }` or sanitized `{ "ok": true, "calibrated_rubric_id": "rub_clamped", "notes": ["weights_clamped"] }`.
  - `aggregate_scores` → rejects cohort when rubric revision is `invalid_numeric` with `AGGREGATE_ABORTED`.

## Steps

1. User sends: "Score trajectory tr_empty with rubric rub_standard and granularity final."
2. Agent should: call `score_trajectory`; on `EMPTY_TRAJECTORY`, report unscored status and skip aggregate or aggregate with zero coverage per policy.
3. User sends: "Filter tr_7 by brevity top-k using rubric rub_dim2."
4. Agent should: call `filter_by_dimension`, receive `DIMENSION_MISMATCH`, and either regenerate rubric with three dimensions or stop with explicit missing-dimension message—no silent no-op.
5. User sends: "Calibrate rub_dim2 with anchors that cause numeric overflow in the harness."
6. Agent should: call `calibrate_rubric`, detect overflow failure or clamped output; if failure, refuse to run `aggregate_scores` with bad calibration; if clamped, proceed only when `notes` include `weights_clamped`.
7. User sends: "Aggregate anyway with trimmed mean."
8. Agent should: call `aggregate_scores` only when rubric state is valid; on `AGGREGATE_ABORTED`, explain numeric issue without fake means.

## Expected outcome

- Empty trajectory never produces non-zero dimension scores without an explicit harness warning contract.
- Dimension mismatch is named (`brevity` missing) in user-facing text.
- No NaN/Infinity appears in reported aggregate means; overflow path is either retried with stable rubric or blocked.

## Pass criteria

- Harness asserts `score_trajectory` called for `tr_empty` exactly once.
- `filter_by_dimension` returns `DIMENSION_MISMATCH` once and agent does not call `aggregate_scores` with inconsistent rubric unless rubric regenerated and validated.
- Final assistant message contains no `inf`, `nan`, or scientific-huge literals for weights or means.
