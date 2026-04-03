# Tool: `create_directory`

## Purpose

Create a directory relative to the workspace root. Creates parent directories when needed (`mkdir -p` semantics).

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["path"],
  "properties": {
    "path": {
      "type": "string",
      "description": "Directory path relative to root."
    },
    "mode": {
      "type": "string",
      "pattern": "^0[0-7]{3}$",
      "description": "Optional Unix mode string e.g. \"0755\"."
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "result": { "path": "by-date/2026/04", "created": true }
}
```

If the directory already exists:

```json
{
  "ok": true,
  "result": { "path": "by-date/2026/04", "created": false }
}
```

## Side effects

Creates zero or more directories.

## Auth / permissions

Write access within `FILE_ORGANIZER_ROOT`.
