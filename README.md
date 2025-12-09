# Beads Village

Multi-agent MCP server for **task coordination** and **file locking** between AI agents.

Combines [Beads](https://github.com/steveyegge/beads) (issue tracking) + Agent Mail (messaging) to enable multiple agents to work on the same codebase without conflicts.

## Use Cases

- **Multi-agent development**: Multiple AI agents working on different parts of a codebase
- **Task queue management**: Agents claim and complete tasks from a shared queue
- **File conflict prevention**: Lock files before editing to prevent merge conflicts
- **Cross-agent communication**: Send messages between agents for coordination

## Installation

```bash
# Option 1: npx (recommended)
npx beads-village

# Option 2: npm global
npm install -g beads-village

# Option 3: pip
pip install beads-village
```

**Requirements**: Python 3.8+, Node.js 16+ (for npx)

## Configuration

### Claude Desktop

`%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "beads-village": {
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

### VS Code / Amp

`.vscode/settings.json`

```json
{
  "amp.mcpServers": {
    "beads-village": {
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

### Cursor

Settings > MCP > Add Server with same config as above.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Shared via Git                          │
│  .beads/        .mail/           .reservations/             │
│  (tasks)        (messages)       (file locks)               │
└─────────────────────────────────────────────────────────────┘
        ▲               ▲                  ▲
        │               │                  │
   ┌────┴────┐    ┌─────┴────┐      ┌──────┴─────┐
   │ Agent 1 │    │ Agent 2  │      │  Agent 3   │
   │ (FE)    │    │ (BE)     │      │  (Mobile)  │
   └─────────┘    └──────────┘      └────────────┘
```

All agents share task queue, messages, and file locks through Git-synced directories.

## Issue Types & Priorities

### Types

| Type | Use For | Example |
|------|---------|---------|
| `task` | General work item (default) | "Refactor auth module" |
| `bug` | Defect to fix | "Login fails with special chars" |
| `feature` | New functionality | "Add OAuth2 login" |
| `epic` | Large work with sub-issues | "User authentication system" |
| `story` | User-facing feature | "As a user, I can reset password" |
| `chore` | Maintenance, cleanup | "Update dependencies" |

### Priority Levels

| Priority | Meaning | When to Use |
|----------|---------|-------------|
| 0 | Critical | Production down, security issue |
| 1 | High | Blocking other work |
| 2 | Medium | Normal priority (default) |
| 3 | Low | Nice to have |
| 4 | Backlog | Future consideration |

## Creating Issues

**Always include a description** - issues without context are harder to work on later:

```python
# Basic issue
add(title="Fix login bug", typ="bug", pri=1)

# With description (recommended)
add(
    title="Fix login bug",
    desc="Login fails with 500 error when password has special characters. Found during auth testing.",
    typ="bug",
    pri=1
)

# With dependencies
add(
    title="Add password validation",
    desc="Frontend validation for password strength",
    typ="feature",
    deps=["discovered-from:bd-42", "blocks:bd-50"]
)
```

### Dependency Types

| Type | Meaning | Example |
|------|---------|---------|
| `discovered-from` | Found while working on another issue | `deps=["discovered-from:bd-42"]` |
| `blocks` | This issue blocks another | `deps=["blocks:bd-50"]` |
| `related` | Related but not blocking | `deps=["related:bd-45"]` |
| `parent-child` | Sub-issue of epic | `deps=["parent-child:bd-10"]` |

## Multi-Agent Workflow

Agents can **switch between workspaces** to read tasks from other teams:

```python
# FE agent joins BE workspace to see their APIs
init(ws="/projects/api")
ls(status="closed")  # See completed tasks
show(id="bd-1")      # Read API details

# Switch back to FE workspace
init(ws="/projects/web")
add(title="Login form", desc="Uses /auth/login API from BE", typ="feature")
```

| Aspect | Behavior |
|--------|----------|
| **Switching** | `init(ws="/path")` changes workspace |
| **Storage** | Each workspace has `.beads/`, `.mail/`, `.reservations/` |
| **Cross-team** | Switch → read with `ls()`, `show()` → switch back |

## Workflow

```
init() → claim() → reserve() → [work] → done() → RESTART
```

1. **init()** - Join workspace
2. **claim()** - Get next available task
3. **reserve()** - Lock files before editing
4. **[work]** - Do the actual work
5. **done()** - Complete task, release locks
6. **RESTART** - Start new session (recommended)

## Best Practices

| Practice | Why |
|----------|-----|
| **One task per session** | Restart after `done()` for clean state |
| **Always reserve before editing** | Prevents merge conflicts |
| **File issues for side-discoveries** | `add(title="...", typ="bug")` immediately |
| **Keep <200 open issues** | Run `cleanup(days=2)` regularly |

## Tools

| Category | Tools | Description |
|----------|-------|-------------|
| **Workflow** | `init`, `claim`, `done` | Task lifecycle |
| **Issues** | `add`, `ls`, `ready`, `show` | CRUD operations |
| **File Locking** | `reserve`, `release`, `reservations` | Conflict prevention |
| **Messaging** | `msg`, `inbox` | Agent coordination |
| **Maintenance** | `sync`, `cleanup`, `doctor`, `status` | Housekeeping |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `bd CLI not found` | `go install github.com/steveyegge/beads/cmd/bd@latest` |
| Stale reservations | Run `init()` to cleanup expired |
| >200 open issues | Run `cleanup(days=2)` |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BEADS_AGENT` | `agent-{pid}` | Agent name |
| `BEADS_WS` | Current dir | Workspace path |
| `BEADS_USE_DAEMON` | `1` | Use daemon if available |

## Daemon Support (Optional)

For ~10x faster operations, start the bd daemon:

```bash
bd daemon --start
```

Falls back to CLI automatically if daemon is not running.

| Platform | Support |
|----------|---------|
| Linux/macOS | ✅ Unix socket |
| Windows | ⚠️ Experimental (requires pywin32) |

## Links

- [Beads CLI](https://github.com/steveyegge/beads)
- [Best Practices](https://steve-yegge.medium.com/beads-best-practices-2db636b9760c)

## License

MIT
