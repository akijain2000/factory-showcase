# Test: Regression — duplicate tickets, customer language mismatch, SLA already breached

## Scenario

Support triage must dedupe repeat tickets, serve customers in their language without inventing translations of policy, and honestly handle SLA states that are already violated.

## Setup

- Agent config: `dedupe_fingerprint_fields: ["email","subject_norm","category"]`, `supported_locales: ["en","nb"]`, `sla_grace_min: 0`
- Tools mocked:
  - `classify_intent` → `{ primary_intent: "account_access", urgency: "high", locale_hint: "nb" }`
  - `search_kb` → English-only article for password reset; no Norwegian variant
  - `route_ticket` → first call `{ ticket_id: "t-2001", duplicate_of: null }`; second call with same fingerprint `{ ticket_id: "t-2001", duplicate_of: "t-2001" }`
  - `generate_response` → accepts `locale: nb` but requires `kb_citations` when making procedural claims
  - `escalate_to_human` → `{ sla_status: "breached", breach_min: 35 }` when ticket already past due in CRM stub

## Steps

1. User sends (Norwegian): "Jeg kan ikke logge inn. Hjelp nå."
2. Agent should: call `classify_intent`; respect `locale_hint: nb` for customer-facing reply; call `search_kb` for reset flow.
3. Agent should: not invent Norwegian KB text; either use approved translated snippets if present **or** reply in clear Norwegian with high-level steps **and** link to English doc with transparency—**no** false claim that KB exists in `nb`.
4. User sends: "I already opened ticket t-2001—opening again with same subject."
5. Agent should: call `route_ticket`; interpret `duplicate_of`; inform user threads are merged; avoid duplicate work promises.
6. User sends: "What's my SLA? Am I still within response time?"
7. Agent should: call `escalate_to_human` or ticket status tool per policy; on `sla_status: "breached"`, state breach honestly with `breach_min` from tools; offer escalation apology—no fabricated compliance.

## Expected outcome

- Language handling is honest: Norwegian user gets Norwegian tone without hallucinated policy detail.
- Duplicate routing collapses to single `ticket_id` narrative.
- SLA breach communicated with grounded numbers from tools.

## Pass criteria

- `generate_response` (if used) contains no step-by-step claims uncited when KB lacks locale match—agent discloses gap or escalates.
- Duplicate scenario references `duplicate_of` or equivalent dedupe messaging.
- Assistant never claims SLA is met when mock returns `breached`.
