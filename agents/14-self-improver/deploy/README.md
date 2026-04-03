# Deploy: Self-Improver Agent

## Environment variables

| Name | Required | Description |
|------|----------|-------------|
| `PROMPT_REGISTRY_URI` | yes | Versioned prompt storage with hash concurrency |
| `EVAL_SUITE_REF` | yes | Canonical suite manifest location |
| `METRICS_STORE_URI` | yes | Run summaries and comparison indexes |
| `EVAL_RUNNER_ENDPOINT` | yes | Sandboxed job executor for `run_evaluation` |
| `MODEL_API_ENDPOINT` | yes | Model access for eval worker (secrets via host) |

## Isolation

- Run evaluations in **network-restricted** sandboxes with fixture data only.
- Separate **production** registry namespace from **experiment** namespace.

## Quotas

| Resource | Suggested |
|----------|-----------|
| Concurrent evals | Small pool; queue overflow returns `RUNNER_BUSY` |
| Artifact retention | 30–90 days with lifecycle rules |
| Prompt diff size | Enforce max bytes; reject megabyte-scale churn |

## Governance

- Require `review_ticket_id` for `commit_or_revert: keep` in regulated environments.
- Maintain **rollback_handle** in CMDB; test rollback quarterly.

## Observability

- Metrics: `eval_run_duration_sec`, `gate_pass_rate`, `commit_rate`, `revert_rate`, `suite_version_skew_alerts`.
- Trace: link `run_id`, `candidate_id`, and `compare_report_id` across spans.
