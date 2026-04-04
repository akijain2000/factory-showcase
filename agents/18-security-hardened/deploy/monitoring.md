# Monitoring: Security-Hardened Agent (18)

Detection, sanitization, and audit pipeline. Low-latency spans for `detect_injection`, `sanitize_input`, `validate_output`.

## SLO definitions

| Objective | Target | Measurement window | Notes |
|-----------|--------|--------------------|-------|
| Availability | ≥ 99.9% | 30d | Inline security path |
| Latency p50 / p95 | 20ms / 100ms | 24h | Non-blocking checks where possible |
| Error rate | < 0.1% | 24h | Pipeline internal errors |
| Cost per request | Minimal; alert on LLM-assisted checks | 30d | If secondary model used |
| **Detection latency p99** | **< 5s** | 24h | Request → detection verdict available to router |
| **False positive rate** | **< 1%** | 30d | Labeled review sample; appeals queue |

## Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| DetectionP99 | p99 ≥ 5s for 10m | critical | Path must stay fast; offload heavy scans async if designed |
| FalsePosSpike | FP ≥ 1% rolling | high | Tune rules; rollback policy pack |
| MissedThreats | confirmed misses from IR | sev-1 | Red team; expand detectors |
| AuditLogLag | write lag > 30s | high | Storage; compliance risk |
| SanitizeBypassAttempts | spike in blocked patterns | medium | WAF correlation |

## Dashboard spec

- **Row 1:** Requests/sec, block vs allow, detection latency percentiles.
- **Row 2:** FP/FN rates (sampled), rule hit breakdown.
- **Row 3:** `audit_log` append rate; permission check latency.
- **Breakdowns:** Tenant, channel, policy version.

## Health check endpoint spec

- **GET `/healthz`:** process up.
- **GET `/readyz`:** ruleset loaded; HMAC/signing keys valid; audit sink writable.
- **GET `/security/policy-version`:** active pack id.

## Runbook references

- `deploy/README.md`
- `tests/injection-denied-output-blocked.md`
- `tests/test-error-recovery.md`
