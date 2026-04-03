# Tool: `search_kb`

## Purpose

Retrieve knowledge-base articles and policy snippets with citation ids.

## Invocation

**MCP** tool name: `search_kb`

## Input schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Search string |
| `locale` | string | no | BCP-47 tag |
| `top_k` | integer | no | Default 5 |

## Output schema

| Field | Type | Description |
|-------|------|-------------|
| `hits` | array | `{ article_id, title, excerpt, url }` |

## Errors

- `KB_UNAVAILABLE`
