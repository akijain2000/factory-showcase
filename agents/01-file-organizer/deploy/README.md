# Deploy: File Organizer Agent

## Required environment variables

| Name | Required | Description |
|------|----------|-------------|
| `FILE_ORGANIZER_ROOT` | yes | Absolute path to the allowed workspace root |
| `FILE_ORGANIZER_MAX_STEPS` | no | Max ReAct iterations (default `20`) |
| `MODEL_API_KEY` / provider equivalent | yes* | Model API key (*if not using on-prem) |

Secret **values** must come from your secret manager; do not commit them.

## Health check

Expose `GET /healthz` (or equivalent) on the agent HTTP wrapper:

- Returns `200` when the process is up and `FILE_ORGANIZER_ROOT` is readable.
- Returns `503` if the root is missing or not a directory.

## Resource limits

| Resource | Suggested |
|----------|-----------|
| CPU | 0.5–1 core |
| Memory | 256–512 MiB |
| Request timeout | 60s per user turn |
| Tool timeout | 10s per tool call |

## Runbook pointers

- On repeated `EIO` from tools, check disk space and permissions on `FILE_ORGANIZER_ROOT`.
- On prompt or schema changes, run CI tests that validate tool registration against `tools/*.md`.
