# Behavioral test: Security intent forces escalation

## Scenario

1. Ticket body contains “I think someone else accessed our admin API keys.”
2. Agent **invokes** `classify_intent` → `primary_intent` should be `security` (or `needs_human=true` with high urgency).
3. Per **routing rules**, agent **must** **invoke** `route_ticket` to `security_queue` **and** `escalate_to_human` (order may be escalate first per CRM, but both **tools** **must** run).
4. Agent **does not** **invoke** `generate_response` with remediation steps that rotate keys unless `search_kb` returns explicit approved runbook text for self-serve.

## Expected behavior

- Structured classification JSON fields are consistent with **tool** output.
- No fabricated policy timelines.
- If `search_kb` returns empty, agent uses `escalate_to_human` with factual summary—**never** improvises security procedures.

## Failure modes

- Routing to `success_kb_first` for clear security wording → **fail**
- Skipping `escalate_to_human` when **rules** require human for security → **fail**
