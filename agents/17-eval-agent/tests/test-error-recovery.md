# Test: scoring tool failures, retries, and timeouts

## Scenario

During an evaluation run, `score_trajectory` intermittently returns rate-limit errors, `aggregate_scores` times out once on a large cohort, and `calibrate_rubric` fails closed when the registry is briefly unavailable. The agent retries with backoff, falls back to the last good rubric revision, and completes aggregation with explicit partial-coverage flags.

## Setup

- Agent config: `EVAL_AGENT_RUBRIC_REGISTRY_REF=registry://eval/fixtures`, `EVAL_AGENT_MODEL_ENDPOINT` pointed at harness model, scoring timeout `12000ms`.
- Tools mocked:
  - `generate_rubric` → `{ "validation": { "ok": true }, "rubric_id": "rub_base_7" }`
  - `score_trajectory` → first two calls return `{ "ok": false, "error": "RATE_LIMIT" }`, third succeeds with `{ "ok": true, "scores": {...} }` per trajectory id.
  - `filter_by_dimension` → stable `{ "filtered_ref": "tr_filt_1" }`
  - `calibrate_rubric` → first call `{ "ok": false, "error": "REGISTRY_UNAVAILABLE" }`; second call (after delay) `{ "ok": true, "calibrated_rubric_id": "rub_base_7_rev2" }`
  - `aggregate_scores` → first call times out (harness); second returns `{ "ok": true, "method": "trimmed_mean", "coverage": { "scored": 5, "total": 5 } }`

## Steps

1. User sends: "Score trajectories tr_1–tr_5 with rubric from this spec; calibrate against anchors; aggregate with trimmed mean even if the service is flaky."
2. Agent should: call `generate_rubric`, then `score_trajectory` for each id, retrying on `RATE_LIMIT` with bounded attempts.
3. Agent should: optionally call `filter_by_dimension` when boilerplate is detected; if tools fail, document skipped filter.
4. Agent should: on `REGISTRY_UNAVAILABLE` for `calibrate_rubric`, retry once after backoff or proceed with `rub_base_7` while stating calibration was skipped.
5. Agent should: on `aggregate_scores` timeout, retry once with a smaller trim or reduced cohort per harness allowance, then succeed on second call.
6. Agent should: report final gate status using the calibrated rubric id when present, else base rubric, with explicit note if calibration was deferred.

## Expected outcome

- Every trajectory receives a final score or an explicit `unscored` reason in the user summary.
- No duplicate counting of the same trajectory in `aggregate_scores.coverage`.
- User-visible text states when calibration used `rev2` versus base rubric due to registry outage.

## Pass criteria

- Harness: at least two `score_trajectory` retries total across the batch; at most three attempts per single trajectory.
- `calibrate_rubric` invoked at least twice OR once with documented skip path matching mock.
- `aggregate_scores` succeeds on retry with `coverage.scored == 5`.
