# Beads Village MCP - Quick Reference

## Workflow
```
init() → claim() → reserve(paths) → work → done(id,msg) → restart
```

## Core Tools

| Tool | Use | Key Args |
|------|-----|----------|
| `init` | Join workspace (FIRST) | `ws`, `team` |
| `claim` | Get next task | - |
| `done` | Complete task | `id`, `msg` |
| `add` | Create issue | `title`, `desc`, `typ`, `pri` |

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

## Response Fields

`id`=ID, `t`=title, `p`=priority(0-4), `s`=status, `f`=from, `b`=body

## Priority

0=critical, 1=high, 2=normal, 3=low, 4=backlog

## Types

task, bug, feature, epic, chore

## Rules

1. Always `init()` first
2. Always `reserve()` before editing files
3. Create issues for work >2min
4. Restart session after `done()`
