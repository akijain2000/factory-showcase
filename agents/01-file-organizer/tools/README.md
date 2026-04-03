# Tools: File Organizer Agent

| Tool | Purpose | Side effects |
|------|---------|--------------|
| `list_files` | Enumerate files under a path with optional filters | Read-only |
| `move_file` | Move or rename a file within the root | Mutates filesystem |
| `create_directory` | Create a directory (parents as needed) within the root | Mutates filesystem |

Each tool has a matching `*.md` contract with JSON Schema for arguments and documented return shape.
