# Test: Error recovery — tool failures, retries, timeouts, circuit breaker

## Scenario

During a long curation cycle, `curate_context` times out once, `evaluate_context_quality` returns a transient `STORE_UNAVAILABLE`, and the context store circuit opens after repeated failures. The agent must recover without corrupting bundles or skipping mandatory gates.

## Setup

- Agent config: `CONTEXT_MAX_TOKENS=128000`, `CONTEXT_STORE_URI=mock://context-store`, `PROMPT_VERSION_NAMESPACE=ace/test`, retry policy `max_attempts=3` with exponential backoff, circuit breaker `failure_threshold=3` / `half_open_after_ms=5000`.
- Tools mocked:
  - `curate_context`: first call → timeout after 25s; second call → `{ "bundle_id": "bnd_7k2", "item_count": 42, "est_tokens": 98000 }`.
  - `evaluate_context_quality`: first call → `{ "error": "STORE_UNAVAILABLE", "retryable": true }`; second call → `{ "pass": true, "gaps": [] }`.
  - `compress_context`: `{ "bundle_id": "bnd_7k2", "est_tokens": 72000, "ok": true }`.
  - `reflect_on_output`: `{ "insights": [{ "category": "transient_tool_failure", "note": "curate timeout recovered" }], "ok": true }`.
  - `update_system_prompt`: circuit open path returns `{ "error": "CIRCUIT_OPEN", "retry_after_ms": 5000 }`; after simulated half-open, `{ "dry_run": true, "validation": { "safety_constraints_preserved": true } }`.

## Steps

1. User sends: "Curate yesterday's incident logs for the postmortem summary and compress if we're near the limit."
2. Agent should: invoke `curate_context` with objective and bounds; on timeout, wait per policy and retry (single bounded retry in fixture).
3. Agent should: call `evaluate_context_quality` for `bnd_7k2`; on `STORE_UNAVAILABLE`, retry once without skipping the tool.
4. Agent should: when estimated tokens exceed a safe ratio of `CONTEXT_MAX_TOKENS`, call `compress_context` before proposing prompt changes.
5. Agent should: attempt `update_system_prompt` with `dry_run: true`; on `CIRCUIT_OPEN`, surface the condition, wait or defer per policy, then complete dry-run after breaker allows.

## Expected outcome

- No duplicate `bundle_id` promotion or merge of two partial curations into one inconsistent bundle.
- Quality evaluation is not bypassed; final state shows `evaluate_context_quality.pass === true` before any non-dry-run prompt update (none in this scenario).
- User-facing summary cites tool states (timeout recovered, breaker open/closed) without inventing token counts.
- Audit trail records retry reasons and does not log full raw log payloads.

## Pass criteria

- Exactly one successful `curate_context` after at most one retry; zero silent drops of the curation step.
- At least two `evaluate_context_quality` calls with the second returning `pass: true`.
- On `CIRCUIT_OPEN`, zero live prompt version bumps; dry-run completes only after mocked half-open window.
- Measurable: fixture asserts call order `curate → evaluate → (compress if triggered) → update_system_prompt` with no `update_system_prompt` before successful evaluate.
