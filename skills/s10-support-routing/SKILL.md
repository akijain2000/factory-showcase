---
name: s10-support-routing
description: Analyzes inbound support intents and applies routing rules to queues, macros, or escalations. Use when tickets arrive unstructured or the support-triage agent assigns work.
---

# Support intent classification and routing

## Goal / overview

Turn noisy customer messages into labeled intents with the right queue, priority, and macro so humans spend time on exceptions, not sorting. Pairs with agent `10-support-triage`.

## When to use

- A shared inbox mixes billing, bugs, access, and security reports.
- SLAs differ by product tier or severity.
- Automated replies must avoid sending unsafe instructions.

## Steps

1. Normalize the message: strip signatures, detect language, extract account or order identifiers when present.
2. Tag intent using a fixed taxonomy (e.g. `billing`, `bug`, `access`, `how-to`, `security`, `spam`); allow at most two secondary tags.
3. Score urgency from signals: money movement, data exposure, widespread outage keywords, or explicit legal threats—override default priority when matched.
4. Apply routing rules table: intent × tier × region → queue, group, or specialist; log the rule id applied.
5. Select a response template or draft: include only verified steps; if knowledge base match confidence is low, route to human instead of guessing.
6. If security-sensitive (credential sharing, RCE claims), force escalation path and suppress auto-close macros.

## Output format

- **Routing record**: ticket id, primary intent, secondary tags, priority, queue, rule id.
- **Customer-facing draft** (optional): subject, body with placeholders filled, disclaimers when unverified.
- **Internal note**: evidence lines from the message that drove the decision.

## Gotchas

- Phishing and social engineering mimic billing issues; never ask for passwords or MFA codes.
- Duplicate tickets from one incident should link to a parent record to avoid conflicting fixes.
- Overbroad regex routes (e.g. any mention of “refund”) mis-route feature questions; review rules periodically.

## Test scenarios

1. **Mixed intent**: Message starts with billing but includes a reproducible bug; output should pick primary intent per policy (e.g. bug if blocking payment) and note both tags.
2. **Security signal**: User pastes API keys; output should escalate, advise rotation, and avoid echoing secrets in replies.
3. **Unknown product**: No account match; output should route to verification queue with a safe macro requesting order id without promising refunds.
