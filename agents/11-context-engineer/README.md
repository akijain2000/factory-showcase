# Context Engineer Agent (ACE Pattern)

An agent specialized in **evolving system prompts**, **context curation**, and **reflection loops**. It implements the **Agent–Context–Evolution (ACE)** pattern: continuously refine what the model sees, how it reasons about failures, and how instructions compress over long sessions.

## Audience

Platform engineers and prompt architects who run long-horizon assistants and need **bounded context**, **auditable prompt changes**, and **quality gates** before promoting new system text.

## Quickstart

1. Load `system-prompt.md` into your host runtime.
2. Register tools from `tools/` with schemas matching each markdown specification.
3. Run `src/agent.py` as a reference loop; wire your LLM client and persistence per `deploy/README.md`.

## Configuration

| Variable | Description |
|----------|-------------|
| `CONTEXT_STORE_URI` | Durable store for curated windows and prompt versions |
| `CONTEXT_MAX_TOKENS` | Hard ceiling for working context after curation |
| `MODEL_API_ENDPOINT` | Upstream chat/completions endpoint (no secrets in repo) |
| `PROMPT_VERSION_NAMESPACE` | Logical namespace for `update_system_prompt` drafts |

## Architecture

```
                         +----------------------+
                         |   User / upstream    |
                         |   task + raw logs    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   curate_context     |
                         | (select / structure  |
                         |  evidence windows)   |
                         +----------+-----------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
 +-------------------+   +-------------------+   +-------------------+
 | evaluate_context_ |   | reflect_on_output |   | compress_context|
 | quality           |   | (failure / success|   | (lossy merge,   |
 | (scores + gaps)   |   |  structured notes)  |   |  summaries)     |
 +---------+---------+   +---------+---------+   +---------+---------+
           |                       |                       |
           +-----------------------+-----------+-----------+
                                               |
                                               v
                                    +----------------------+
                                    | update_system_prompt |
                                    | (draft -> review ->  |
                                    |  version bump)       |
                                    +----------+-----------+
                                               |
                         +---------------------+---------------------+
                         |                                           |
                         v                                           v
                +----------------+                         +----------------+
                | Next turn uses |<---- evolution loop ---->| Audit / rollback|
                | promoted prompt|                         | (host policy)   |
                +----------------+                         +----------------+
```

## Operational loop

1. **Curate** incoming traces into ranked, citeable chunks.
2. **Reflect** on the last model output against task success criteria.
3. **Evaluate** context quality before expensive generation.
4. **Compress** when approaching token limits; preserve constraints and tool contracts.
5. **Evolve** system prompt only when metrics and human or automated review allow.

## Testing

See `tests/` for end-to-end behavioral scenarios.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
