# Monitoring: Support Triage Agent

Real-time ticket triage — strict latency SLO; errors directly hit customer wait time.

## Service level objectives (SLOs)

| Dimension | Target | Window / scope |
|-----------|--------|----------------|
| Availability | ≥ 99.5% | Rolling 30 days |
| Latency p50 | < 1.5 s | Per ticket |
| Latency p95 | < 3 s | Per ticket |
| Latency p99 | < 5 s | Per ticket |
| Error rate | < 2% | Rolling 24 h |
| Cost per successful request | < $0.02 USD | Daily rollup (high volume) |

## Alert rules

| ID | Condition | Severity | For |
|----|-----------|----------|-----|
| A1 | Error rate > 5% for 5 minutes | Page | Queue stalls |
| A2 | Error rate > 2% for 15 minutes | Warning | SLO burn |
| A3 | Latency p99 > 5 s for 5 minutes | Page | Breach of “real-time” feel |
| A4 | Spend > $75 / day | Warning | Ticket storm or oversized threads |

## Dashboard specification

**Board: Support Triage – Production**

- **Time ranges:** 15 m, 1 h, 24 h.
- **Row 1:** Tickets/min, backlog depth, first-response SLA compliance.
- **Row 2:** p50 / p95 / p99 end-to-end; queue wait vs. model time.
- **Row 3:** $/1k tickets, token use, cache hit rate for similar tickets.
- **Row 4:** CRM / helpdesk API errors, webhook retries.
- **Breakdowns:** By channel (email/chat), priority, language.

## Health check endpoint

`GET /health`

```json
{
  "status": "ok",
  "agent": "support-triage",
  "version": "1.0.0",
  "checks": {
    "process": "up",
    "helpdesk_api": "reachable",
    "model_endpoint": "reachable",
    "rate_limiter": "ok"
  }
}
```

## Runbook references

| Alert | Runbook |
|-------|---------|
| A1, A2 | `deploy/runbooks/support-triage-error-rate.md` |
| A3 | `deploy/runbooks/support-triage-latency.md` — edge cache, trim ticket bodies |
| A4 | `deploy/runbooks/support-triage-cost.md` |
