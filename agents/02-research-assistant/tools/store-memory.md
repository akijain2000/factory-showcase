# Tool: `store_memory`

## Purpose

Persist durable **research context** for the session or user (hypotheses, source lists, follow-ups).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["key", "content"],
  "properties": {
    "key": {
      "type": "string",
      "pattern": "^[a-z0-9._-]{1,64}$",
      "description": "Stable key, e.g. session.open_questions"
    },
    "content": { "type": "string", "maxLength": 32000 },
    "ttl_seconds": { "type": "integer", "minimum": 60, "maximum": 2592000 },
    "pii": { "type": "boolean", "default": false, "description": "Must be false unless policy allows" }
  }
}
```

## Return shape

```json
{ "ok": true, "stored": true, "key": "session.open_questions", "version": 3 }
```

## Side effects

Writes to memory backend.

## Constraints

Implementations **must reject** `pii: true` unless enterprise policy enables redacted storage.
