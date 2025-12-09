# Workflow Patterns & Best Practices

Detailed workflows, patterns, and examples for multi-agent coordination.

---

## Table of Contents

- [Standard Workflow](#standard-workflow)
- [Role-Based Workflow](#role-based-workflow)
- [Workflow Patterns](#workflow-patterns)
- [Issue Management](#issue-management)
- [Team Setup](#team-setup)
- [Best Practices](#best-practices)

---

## Standard Workflow

```
init() → claim() → reserve() → [work] → done() → RESTART
```

| Step | Tool | Description |
|------|------|-------------|
| 1 | `init()` | Join workspace, get agent ID |
| 2 | `claim()` | Get next available task |
| 3 | `reserve()` | Lock files before editing |
| 4 | - | Do the actual work |
| 5 | `done()` | Complete task, release locks |
| 6 | RESTART | Start new session (recommended) |

---

## Role-Based Workflow

### Leader Agent

```python
# 1. Initialize as leader
init(team="my-project", leader=true)

# 2. Create tasks with role tags
add(title="Build user API", tags=["be"], pri=1)
add(title="User profile page", tags=["fe"], pri=1)
add(title="Setup CI pipeline", tags=["devops"], pri=2)

# 3. Monitor progress
ls(status="in_progress")
discover()  # See active agents
```

### Worker Agent

```python
# 1. Initialize with role
init(team="my-project", role="fe")

# 2. Claim task (auto-filtered by role)
claim()  # Only gets tasks tagged "fe"

# 3. Reserve files
reserve(paths=["src/components/Profile.tsx"], reason="bd-42")

# 4. Do work...

# 5. Complete
done(id="bd-42", msg="Profile page complete")
```

### Available Roles

| Role | Description | Typical Files |
|------|-------------|---------------|
| `fe` | Frontend | `*.tsx`, `*.vue`, `*.css` |
| `be` | Backend | `*.py`, `*.go`, `*.java` |
| `mobile` | Mobile apps | `*.swift`, `*.kt` |
| `devops` | Infrastructure | `Dockerfile`, `*.yaml` |
| `qa` | Testing | `*.test.*`, `*.spec.*` |

---

## Workflow Patterns

### Pattern 1: Standard Task Completion

```python
init()
claim()  
# {"id":"bd-42", "t":"Add login", "p":1, "s":"in_progress"}

reserve(paths=["src/auth.py", "src/login.py"], reason="bd-42", ttl=600)
# {"granted":["src/auth.py","src/login.py"], "conflicts":[]}

# [implement feature]

done(id="bd-42", msg="Implemented login with JWT tokens")
# {"ok":1, "done":1, "hint":"restart session"}
```

### Pattern 2: Finding Side Issues

```python
# While working on bd-42, discover a bug
add(
    title="Password validation missing",
    desc="Found during login implementation (bd-42). No min length validation.",
    typ="bug",
    pri=2,
    tags=["be"],
    parent="bd-42"
)
# Continue with original task
done(id="bd-42", msg="Login done. Filed bd-43 for password validation.")
```

### Pattern 3: Cross-Workspace Coordination

```python
# === BE Agent ===
init(team="ecommerce", role="be")
claim()  # Gets API task
# [implement API]
done(id="bd-10", msg="Login API ready")
broadcast(subj="Auth API Ready", body="POST /auth/login returns JWT")

# === FE Agent ===
init(team="ecommerce", role="fe")
inbox()  # Sees broadcast from BE agent
claim()  # Gets UI task
# [implement form using the API]
done(id="bd-11", msg="Login form complete")
```

### Pattern 4: Handling Conflicts

```python
# Check before reserving
reservations()
# [{"path":"src/api.py", "agent":"agent-2", "expires":"..."}]

# File locked - options:
# 1. Wait and check again
# 2. Message the agent
msg(subj="Need src/api.py", body="Working on bd-50", to="agent-2")
# 3. Work on something else
claim()
```

### Pattern 5: Handling Blocked Tasks

```python
claim()  # Gets a task, but discover it's blocked

# 1. Create blocker issue
add(
    title="Need database schema update",
    desc="bd-42 blocked until users table has email column",
    typ="task",
    pri=1
)

# 2. Release files and move on
release()
claim()  # Get different task
```

---

## Issue Management

### Issue Types

| Type | Use For | Example |
|------|---------|---------|
| `task` | General work (default) | "Refactor auth module" |
| `bug` | Something broken | "Login fails on Safari" |
| `feature` | New functionality | "Add OAuth2 support" |
| `epic` | Large work with sub-tasks | "User authentication system" |
| `story` | User-facing capability | "As a user, I can reset password" |
| `chore` | Maintenance | "Update npm dependencies" |

### Priority Levels

| Priority | Meaning | When to Use |
|----------|---------|-------------|
| **0** | Critical | Production down, security breach |
| **1** | High | Blocking other work |
| **2** | Medium | Normal priority (default) |
| **3** | Low | Nice to have |
| **4** | Backlog | Future consideration |

### Creating Good Issues

```python
# ❌ Bad - no context
add(title="Fix bug")

# ✅ Good - includes context
add(
    title="Fix auth bug",
    desc="Login fails with 500 when password has special chars. Found during bd-42.",
    typ="bug",
    pri=1,
    tags=["be"]
)
```

### Dependency Types

| Type | Meaning | Example |
|------|---------|---------|
| `discovered-from` | Found while working on issue | `deps=["discovered-from:bd-42"]` |
| `blocks` | This blocks another | `deps=["blocks:bd-50"]` |
| `related` | Related but not blocking | `deps=["related:bd-45"]` |
| `parent-child` | Sub-issue of epic | `deps=["parent-child:bd-10"]` |

---

## Team Setup

### Creating/Joining Teams

Teams group agents working on the same project. Teams are created automatically:

```python
# Join/create team
init(team="my-project")
# {"ok":1, "agent":"agent-001", "team":"my-project", "available_teams":["default","my-project"]}

discover()  # See teammates
broadcast(subj="Hello", body="I joined!")  # Notify team
```

### Multi-Agent Team Example

```python
# === Leader creates tasks ===
init(team="ecommerce", leader=true)
add(title="Auth API", tags=["be"], pri=1)
add(title="Login form", tags=["fe"], pri=1)
add(title="Login screen", tags=["mobile"], pri=2)

# === Workers join with roles ===
init(team="ecommerce", role="be")     # Agent 1
init(team="ecommerce", role="fe")     # Agent 2
init(team="ecommerce", role="mobile") # Agent 3

# Each agent's claim() returns matching tasks
```

### Switching Teams

```python
# Working in team alpha, need to check team beta
init(team="beta")
inbox()      # See beta messages
discover()   # See beta agents

# Switch back
init(team="alpha")
```

### Team Data Storage

```
~/.beads-village/
├── ecommerce/          # Team A
│   ├── mail/           # Team broadcasts
│   └── agents/         # Team registry
├── internal-tools/     # Team B (isolated)
└── default/            # Unassigned agents
```

### Scope Comparison

| Scope | Directory | Who Sees |
|-------|-----------|----------|
| **Local** | `/workspace/.mail/` | This workspace only |
| **Team** | `~/.beads-village/{team}/` | All team workspaces |

---

## Best Practices

### Before Starting

- [ ] Call `init()` first (with `role` or `leader`)
- [ ] Check `inbox()` for updates
- [ ] Run `ready()` to see available tasks

### During Work

- [ ] Always `reserve()` before editing
- [ ] Create issues for side-discoveries
- [ ] Keep reservations short (TTL 600s default)
- [ ] Check `reservations()` before editing new files

### When Completing

- [ ] Use descriptive `msg` in `done()`
- [ ] `broadcast()` important completions
- [ ] Restart session after `done()`

### Maintenance (Every Few Days)

- [ ] Run `cleanup(days=2)` to remove old issues
- [ ] Run `doctor()` to fix database issues
- [ ] Keep <200 open issues for performance

---

## Common Mistakes

### ❌ Not calling init() first
```python
claim()  # ERROR: workspace not initialized
# ✅ Fix: init() first
```

### ❌ Editing without reservation
```python
# May cause conflicts with other agents
# ✅ Fix: reserve() before editing
```

### ❌ Using msg() instead of broadcast()
```python
msg(subj="API ready")  # Only local workspace
# ✅ Fix: broadcast() for team-wide announcements
```

### ❌ Not releasing files when switching
```python
reserve(paths=["file.py"])
claim()  # Files still locked!
# ✅ Fix: release() before switching tasks
```

---

[← Back to README](../README.md) | [AGENTS.md](../AGENTS.md) | [AGENTS-LITE.md](../AGENTS-LITE.md)
