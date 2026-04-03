# A2A Coordinator Agent (Agent-to-Agent)

An agent that orchestrates **multi-agent work**: **discovers** peers, **negotiates** interaction protocols, **delegates** subtasks, **aggregates** results, and **resolves conflicts** when outputs disagree.

## Audience

Teams building **federated agent meshes** across services, vendors, or organizational boundaries where capabilities differ and contracts must be explicit.

## Quickstart

1. Load `system-prompt.md`.
2. Register tools against your agent directory and message bus.
3. Use `src/agent.py` as a reference orchestration loop.

## Configuration

| Variable | Description |
|----------|-------------|
| `AGENT_DIRECTORY_URI` | Capability registry and health |
| `A2A_MESSAGE_BUS_REF` | Transport for delegated tasks |
| `POLICY_GATE_REF` | Org rules for cross-agent data sharing |
| `MODEL_API_ENDPOINT` | Coordinator’s reasoning endpoint |

## Architecture

```
 +------------------+
 | Task intake      |
 +--------+---------+
          |
          v
 +------------------+     discover_agents     +------------------+
 | Capability       |------------------------>| Agent directory  |
 | matching plan    |                         | (skills, SLOs)     |
 +--------+---------+                         +------------------+
          |
          v
 +------------------+ negotiate_protocol +------------------+
 | Protocol         |-------------------->| Peer agents      |
 | selection        |                     | (schemas, auth)    |
 +--------+---------+                     +------------------+
          |
          v
 +------------------+ delegate_task +------------------+
 | Work breakdown   |-------------->| Workers          |
 | + partial orders |               | (parallel runs)  |
 +--------+---------+               +------------------+
          |                                  |
          v                                  v
 +------------------+ collect_results +------------------+
 | Aggregation      |<----------------| Result streams   |
 | + normalization  |                 | (typed payloads) |
 +--------+---------+                 +------------------+
          |
          v
 +------------------+ resolve_conflicts +------------------+
 | Final answer      |---------------->| Tie-breakers /   |
 | synthesis         |                 | human escalation |
 +------------------+-----------------+------------------+
```

## Principles

- **Explicit contracts:** JSON Schema or equivalent per delegation.
- **Least privilege:** data minimization in `delegate_task`.
- **Deterministic conflict policy:** prefer evidence-backed merges first.

## Testing

See `tests/` for protocol mismatch and conflict resolution.

## Related files

- `system-prompt.md`, `tools/`, `src/agent.py`, `deploy/README.md`
