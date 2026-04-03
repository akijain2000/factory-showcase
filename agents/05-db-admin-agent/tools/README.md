# Tools: Database Admin Agent

| Tool | Risk | Notes |
|------|------|-------|
| `query_db` | Medium | Profiled: SELECT-only in RO deployments |
| `explain_query` | Low | Planning / EXPLAIN |
| `backup_table` | Medium | Storage + IO; audit logged |
| `execute_ddl` | **Critical** | **HITL** + policy + optional backup prerequisite |

All tools are defined in `*.md` with JSON Schema.
