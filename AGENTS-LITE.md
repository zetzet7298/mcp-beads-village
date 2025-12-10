# Beads Village MCP - Quick Reference

## Workflow

### Leader Agent
```
init(team, leader=true, start_tui=true) → add(tags=["role"]) → assign(id,role) → monitor
```

### Worker Agent
```
init(team, role="fe/be/mobile") → claim() → reserve(paths) → work → done(id,msg) → restart
```

## Dashboard

```bash
python -m beads_village.dashboard [workspace]   # Manual launch
init(leader=true, start_tui=true)              # Auto-launch for leader
```

## Core Tools

| Tool | Use | Key Args |
|------|-----|----------|
| `init` | Join workspace (FIRST) | `ws`, `team`, `role`, `leader`, `start_tui` |
| `claim` | Get next task (filtered by role) | - |
| `done` | Complete task | `id`, `msg` |
| `add` | Create issue | `title`, `desc`, `typ`, `pri`, `tags` |
| `assign` | Assign to role (leader only) | `id`, `role` |

## Query Tools

| Tool | Use |
|------|-----|
| `ls` | List issues (status=open/closed/all) |
| `ready` | Get claimable tasks |
| `show` | Get issue details (id) |

## File Locking

| Tool | Use |
|------|-----|
| `reserve` | Lock files (paths[], ttl, reason) |
| `release` | Unlock files |
| `reservations` | Check locks |

## Messaging

| Tool | Use |
|------|-----|
| `msg` | Send message (subj, to, global) |
| `inbox` | Get messages |
| `broadcast` | Team-wide announcement |
| `discover` | Find agents in team |

## Maintenance

| Tool | Use |
|------|-----|
| `sync` | Git sync |
| `cleanup` | Remove old issues (days) |
| `doctor` | Fix database |
| `status` | Workspace overview |

## Optional: bv Tools
`bv_insights`, `bv_plan`, `bv_priority`, `bv_tui` - Graph analysis (requires bv binary)

## Response Fields

`id`=ID, `t`=title, `p`=priority(0-4), `s`=status, `f`=from, `b`=body, `tags`=role tags

## Priority

0=critical, 1=high, 2=normal, 3=low, 4=backlog

## Types

task, bug, feature, epic, chore

## Role Tags

`fe`=frontend, `be`=backend, `mobile`, `devops`, `qa`

## Rules

1. Always `init()` first
2. Leader: `init(leader=true)` to assign tasks
3. Worker: `init(role="fe/be/...")` to auto-filter tasks
4. Always `reserve()` before editing files
5. Create issues for work >2min
6. Restart session after `done()`

## Example: Multi-Agent Setup

```python
# Leader creates tasks
init(team="proj", leader=true)
add(title="Login API", tags=["be"])
add(title="Login form", tags=["fe"])

# BE agent claims BE tasks
init(team="proj", role="be")
claim()  # Gets "Login API"

# FE agent claims FE tasks
init(team="proj", role="fe")
claim()  # Gets "Login form"
```
