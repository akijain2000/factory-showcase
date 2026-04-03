# Security-Hardened Agent

A **defense-in-depth** agent wrapper that sanitizes untrusted inputs, detects injection patterns, enforces **least-privilege** tool access, validates structured outputs, and emits **audit trails** suitable for regulated environments.

## Audience

Security engineers and platform teams who need an LLM agent that fails **closed** on ambiguous policy, never silently escalates privileges, and produces evidence for compliance reviews.

## Quickstart

1. Load `system-prompt.md` as the outer policy layer.
2. Implement tools in `tools/` as **mandatory gates** around a smaller inner agent.
3. Configure `MODEL_API_ENDPOINT` and policy bundle per `deploy/README.md`.
4. Run `tests/injection-denied-output-blocked.md`.

## Configuration

| Variable | Description |
|----------|-------------|
| `SECURITY_AGENT_POLICY_BUNDLE_REF` | Signed policy document location |
| `SECURITY_AGENT_AUDIT_SINK_REF` | Append-only audit log destination |
| `MODEL_API_ENDPOINT` | Inner model router (no secrets in env values) |

## Architecture

```
          +-------------+
          | Raw input   |
          +------+------+
                 |
                 v
          +-------------+
          | Sanitizer   |
          +------+------+
                 |
                 v
          +-------------------+
          | Injection detector|
          +---------+---------+
                    |
                    v
          +-------------------+
          | Permission check  |
          +---------+---------+
                    |
                    v
          +-------------------+
          |   Agent core      |
          | (narrow tools)    |
          +---------+---------+
                    |
                    v
          +-------------------+
          | Output validator  |
          +---------+---------+
                    |
                    v
          +-------------------+
          | Audit logger      |
          +-------------------+
                    |
                    v
          +-------------------+
          | Released response |
          +-------------------+
```

## Guarantees (design targets)

- **Default deny** for tools not explicitly allowed for the session principal.
- **Schema-first** outputs: validator rejects malformed or oversized payloads.
- **Tamper-evident** audit entries with hash chaining where supported by the sink.

## Testing

See `tests/injection-denied-output-blocked.md`.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
