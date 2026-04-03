# Tool: `define_dag`

## Purpose

Register a **directed acyclic workflow**: steps, dependencies, optional parallelism hints, and per-step durability / timeout requirements.

## JSON Schema (arguments)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["dag_id", "revision", "nodes", "edges"],
  "properties": {
    "dag_id": { "type": "string", "maxLength": 128 },
    "revision": { "type": "integer", "minimum": 1 },
    "nodes": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "action"],
        "properties": {
          "id": { "type": "string", "maxLength": 128 },
          "action": { "type": "string", "maxLength": 128 },
          "timeout_ms": { "type": "integer", "minimum": 100, "maximum": 86400000 },
          "durability": {
            "type": "string",
            "enum": ["best_effort", "required"],
            "default": "required"
          },
          "parallel_group": { "type": "string", "maxLength": 64 }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["from", "to"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "condition": { "type": "string", "description": "Optional named branch tag" }
        }
      }
    }
  }
}
```

## Return shape

```json
{
  "ok": true,
  "dag_id": "wf_invoice",
  "revision": 3,
  "layers": [["ingest", "validate"], ["transform"], ["publish"]],
  "validation": { "acyclic": true, "warnings": [] }
}
```

## Side effects

- Persists DAG spec to registry; rejects duplicate `dag_id`+`revision`.
- Precomputes **execution layers** for parallel scheduling.
