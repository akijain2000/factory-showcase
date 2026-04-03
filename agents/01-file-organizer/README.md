# File Organizer Agent

A minimal **ReAct** agent that organizes files in a target directory by **type** (extension), **modified date**, or **project** (path prefix). Suitable as a template for the smallest AGENT_SPEC–compliant agent package.

## Audience

Developers and operators who want predictable, tool-grounded file moves with explicit arguments—no shell injection via a single “do anything” tool.

## Quickstart

1. Copy this package into your runtime (or mount it as a workspace).
2. Load `system-prompt.md` as the system message.
3. Register tools from `tools/` with your orchestrator; implement handlers in `src/`.
4. Run behavioral checks described in `tests/`.

## Configuration

| Variable | Description |
|----------|-------------|
| `FILE_ORGANIZER_ROOT` | Absolute path cap; the agent must not operate outside this root. |
| `FILE_ORGANIZER_MAX_STEPS` | Upper bound on ReAct iterations per run (default: 20). |

## Architecture

High-level flow: the model plans with **Reasoning + Acting**, calls typed tools, observes structured results, and stops when the user goal is satisfied or limits are hit.

```
                    +------------------+
                    |   User / API     |
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    |  Orchestrator    |
                    |  (ReAct loop)    |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
       +-----------+ +-----------+ +---------------+
       | list_files| | move_file | |create_directory|
       +-----+-----+ +-----+-----+ +-------+-------+
             |             |               |
             v             v               v
       +-----------------------------------------+
       |           Local filesystem            |
       |     (bounded by FILE_ORGANIZER_ROOT)    |
       +-----------------------------------------+
```

## Testing

See `tests/` for scenario-based behavioral specs. Implementations should map these to automated tests (mocked FS) in CI.

## Related files

- `system-prompt.md` — agent instructions
- `tools/` — tool contracts
- `src/` — loop and tool adapters
- `deploy/` — deployment and ops notes
