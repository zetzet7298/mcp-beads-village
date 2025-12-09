# AGENTS.md - Beads Village

## AI Agent Guide for Multi-Agent Task Coordination

This guide helps AI agents use Beads Village MCP correctly for task management and multi-agent coordination.

---

## ⚡ Quick Start (MUST DO FIRST)

```
1. init()              → Join workspace, get agent ID
2. claim()             → Get next ready task
3. reserve(paths=[...]) → Lock files before editing
4. [do work]           → Make changes
5. done(id="...", msg="...") → Complete task
6. RESTART SESSION     → One task = one session (best practice)
```

**CRITICAL**: Always call `init()` BEFORE any other Beads tool!

---

## 🎯 Decision Tree: Which Tool to Use?

### Starting a Session
```
Q: Am I starting work?
├─ Yes → init() first, ALWAYS
└─ Already called init() → proceed to claim() or ready()
```

### Getting Work
```
Q: What task should I work on?
├─ Want next priority task → claim()
├─ Want to see options first → ready(limit=5)
├─ Looking for specific task → ls(status="open") or show(id="...")
└─ No tasks available → add(title="...", desc="...")
```

### Before Editing Files
```
Q: Am I about to edit files?
├─ Yes → reservations() first to check conflicts
│   ├─ No conflicts → reserve(paths=[...], reason="bd-xxx")
│   └─ Conflicts exist → WAIT or coordinate via msg()
└─ Just reading → No reservation needed
```

### Communicating with Other Agents
```
Q: Who needs this message?
├─ Agents in THIS workspace only → msg(subj="...", to="all")
├─ ALL agents in my TEAM (across workspaces) → broadcast(subj="...", body="...")
├─ Specific agent in team → msg(subj="...", to="agent-id", global=true)
└─ Find who's available → discover()
```

### Completing Work
```
Q: Is the task done?
├─ Yes, fully complete → done(id="...", msg="what I did")
├─ Blocked by something → Add blocker issue, switch tasks
├─ Found side work (>2 min) → add(title="...", typ="bug/task")
└─ Need to pause → release() files, don't call done()
```

---

## ⚠️ Common Mistakes & How to Avoid Them

### ❌ Mistake 1: Not calling init() first
```
# WRONG - will fail
claim()  → ERROR: workspace not initialized

# CORRECT
init()   → {"ok":1, "agent":"agent-123", "ws":"/path", "team":"default"}
claim()  → works!
```

### ❌ Mistake 2: Editing files without reservation
```
# WRONG - may cause conflicts with other agents
[edit src/auth.py directly]

# CORRECT
reservations()  → check for conflicts first
reserve(paths=["src/auth.py"], reason="bd-42")
[now safe to edit]
```

### ❌ Mistake 3: Creating issues without description
```
# WRONG - no context for future
add(title="Fix bug")

# CORRECT - includes context
add(
    title="Fix auth bug",
    desc="Login fails with 500 when password has special chars. Found during bd-42.",
    typ="bug",
    pri=1
)
```

### ❌ Mistake 4: Not releasing files when switching tasks
```
# WRONG - blocks other agents
reserve(paths=["src/api.py"])
[decide to work on something else]
claim()  # files still locked!

# CORRECT
reserve(paths=["src/api.py"])
[decide to switch]
release()  # free the files
claim()
```

### ❌ Mistake 5: Using msg() instead of broadcast() for team-wide announcements
```
# WRONG - only reaches local workspace
msg(subj="API ready")

# CORRECT - reaches ALL agents across ALL workspaces in team
broadcast(subj="API ready", body="POST /auth/login is live")
```

### ❌ Mistake 6: Forgetting to sync
```
# WRONG - working on stale data
[make changes]
[other agent's changes are lost]

# CORRECT
sync()  → get latest from git
[make changes]
done()  → auto-syncs
```

---

## 🔄 Workflow Patterns

### Pattern 1: Standard Task Completion
```python
# 1. Initialize
init()

# 2. Get task
claim()  
# Returns: {"id":"bd-42", "t":"Add login", "p":1, "s":"in_progress"}

# 3. Reserve files
reserve(paths=["src/auth.py", "src/login.py"], reason="bd-42", ttl=600)
# Returns: {"granted":["src/auth.py","src/login.py"], "conflicts":[]}

# 4. Do the work
[implement the feature]

# 5. Complete
done(id="bd-42", msg="Implemented login with JWT tokens")
# Returns: {"ok":1, "done":1, "hint":"restart session"}

# 6. RESTART SESSION for next task
```

### Pattern 2: Finding Side Issues During Work
```python
# While working on bd-42, discover a bug
add(
    title="Password validation missing",
    desc="Found during login implementation (bd-42). No validation for min length.",
    typ="bug",
    pri=2,
    parent="bd-42"  # Link to parent task
)
# Returns: {"id":"bd-43", "t":"Password validation missing"}

# Continue with original task
done(id="bd-42", msg="Login done. Filed bd-43 for password validation.")
```

### Pattern 3: Cross-Workspace Coordination (BE/FE)
```python
# === BE Agent in /api workspace ===
init()
claim()  # Gets "Implement /auth/login endpoint"
[implement API]
done(id="bd-10", msg="Login API ready")
broadcast(subj="Auth API Ready", body="POST /auth/login - returns JWT token in 'token' field")

# === FE Agent in /web workspace ===
init()
inbox()  # Sees broadcast from BE agent
# [{"f":"agent-be", "s":"Auth API Ready", "ws":"/api", "global":true}]

discover()  # See who's working
# {"agents":[{"agent":"agent-be","ws":"/api"}, {"agent":"agent-fe","ws":"/web"}]}

# Can switch to BE workspace to see their task details
init(ws="/api")
show(id="bd-10")  # Read API implementation details

# Switch back and create FE task
init(ws="/web")
add(title="Login form", desc="Uses /auth/login from BE", typ="feature")
```

### Pattern 4: Handling Conflicts
```python
# Check before reserving
reservations()
# Returns: [{"path":"src/api.py", "agent":"agent-2", "expires":"..."}]

# File is locked by another agent - DO NOT force edit!
# Option 1: Wait and check again
# Option 2: Message the agent
msg(subj="Need src/api.py", body="Working on bd-50, need to modify api.py", to="agent-2")

# Option 3: Work on something else
claim()  # Get different task
```

### Pattern 5: Handling Blocked Tasks
```python
claim()  # Gets a task
# Discover it's blocked by something

# 1. Create blocker issue
add(
    title="Need database schema update",
    desc="bd-42 blocked until users table has email column",
    typ="task",
    pri=1
)

# 2. Don't complete the blocked task - release and move on
release()
# Task stays in_progress - another agent can pick it up later or you can resume

# 3. Optionally claim different work
claim()
```

---

## 📊 Tool Quick Reference

### Lifecycle Tools
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `init` | Start of EVERY session | `ws="/path"` (optional) | `{ok, agent, ws, team}` |
| `claim` | Get next task to work on | - | `{id, t, p, s}` or `{ok:0, msg}` |
| `done` | Task complete | `id`, `msg` | `{ok, done, hint}` |

### Issue Management
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `add` | Create new issue | `title`, `desc`, `typ`, `pri` | `{id, t, p, typ}` |
| `ls` | List issues | `status`, `limit` | `[{id, t, p, s}...]` |
| `ready` | See claimable tasks | `limit` | `[{id, t, p}...]` |
| `show` | Get issue details | `id` | Full issue object |

### File Locking
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `reserve` | Before editing files | `paths[]`, `reason`, `ttl` | `{granted, conflicts}` |
| `release` | Done editing / switching | `paths[]` (optional) | `{released}` |
| `reservations` | Check what's locked | - | `[{path, agent, expires}...]` |

### Messaging
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `msg` | Direct message | `subj`, `body`, `to`, `global` | `{sent}` |
| `broadcast` | Team announcement | `subj`, `body` | `{sent, global:true}` |
| `inbox` | Check messages | `n`, `unread`, `global` | `[{f, s, b, ts}...]` |

### Discovery & Status
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `discover` | Find teammates | - | `{agents, workspaces}` |
| `status` | Workspace overview | - | `{team, agents, issues...}` |

### Maintenance
| Tool | When to Use | Key Args | Returns |
|------|-------------|----------|---------|
| `sync` | Force git sync | - | `{ok}` |
| `cleanup` | Remove old closed issues | `days` | `{deleted}` |
| `doctor` | Fix database issues | - | Health report |

---

## 🏷️ Issue Types & When to Use

| Type | Use For | Example |
|------|---------|---------|
| `task` | General work (DEFAULT) | "Refactor auth module" |
| `bug` | Something broken | "Login fails on Safari" |
| `feature` | New functionality | "Add OAuth2 support" |
| `epic` | Large work with sub-tasks | "User authentication system" |
| `story` | User-facing capability | "As a user, I can reset password" |
| `chore` | Maintenance | "Update npm dependencies" |

## 🎯 Priority Levels

| Priority | Meaning | When to Use |
|----------|---------|-------------|
| **0** | Critical | Production down, security breach |
| **1** | High | Blocking other work |
| **2** | Medium | Normal priority (DEFAULT) |
| **3** | Low | Nice to have |
| **4** | Backlog | Future consideration |

---

## 🤝 Team Setup

### What is a Team?

A **team** groups related agents (BE, FE, Mobile, etc.) working on the same project. Agents in the same team can:
- See each other via `discover()`
- Send broadcasts via `broadcast()`
- Receive team messages via `inbox()`

Agents in **different teams** are completely isolated - they cannot see or message each other.

### How to Create/Join a Team

**Teams are created automatically** when the first agent joins. Use `init(team="...")` to join:

```python
# Join/create team "my-project"
init(team="my-project")
# Returns: {"ok":1, "agent":"agent-001", "ws":"...", "team":"my-project", "available_teams":["default","my-project"]}

# Now agent is in team "my-project"
discover()  # See other agents in this team
broadcast(subj="Hello", body="I joined!")  # Send to all team members
```

### Xem Available Teams

```python
init()
# Response includes: "available_teams": ["abc", "default", "ecommerce"]

# Hoặc check status
status()
# Returns: {"team":"current-team", ...}
```

### Join Team Cụ Thể

**Scenario**: User bảo "join team abc"

```python
init(team="abc")
# Returns: {
#   "ok": 1,
#   "agent": "agent-003",
#   "ws": "C:\\Projects\\mobile",
#   "team": "abc",                    # ✓ Đã join team abc
#   "available_teams": ["abc", "default", "xyz"]
# }

# Verify - thấy được các agents khác trong team abc
discover()
# Returns: {"team":"abc", "agents":[
#   {"agent":"agent-001", "ws":"C:\\Projects\\api"},
#   {"agent":"agent-002", "ws":"C:\\Projects\\web"},
#   {"agent":"agent-003", "ws":"C:\\Projects\\mobile"}  # Bạn
# ]}
```

### Switching Between Teams

Agent có thể làm việc với nhiều team trong cùng session:

```python
# Đang ở team alpha, cần check team beta
init(team="beta")
inbox()  # Xem messages từ team beta
discover()  # Xem agents trong team beta

# Quay lại team alpha
init(team="alpha")
broadcast(subj="Done", body="Finished checking beta")
```

**Lưu ý**: Khi switch team, agent sẽ:
- Tự động re-register vào team mới
- Gửi join announcement cho team mới
- `broadcast()`, `inbox()`, `discover()` sẽ scope theo team mới

### Example: Setting Up a 3-Agent Team

```python
# Agent 1 (Backend, workspace /api)
init(team="ecommerce")
# → joins team "ecommerce", team is created automatically

# Agent 2 (Frontend, workspace /web)  
init(team="ecommerce")
# → joins existing team "ecommerce"

# Agent 3 (Mobile, workspace /mobile)
init(team="ecommerce")
# → joins existing team "ecommerce"

# All 3 agents can now:
discover()   # See each other
broadcast()  # Send to all
inbox()      # Receive team messages
```

### Default Team

Nếu không chỉ định team, agent sẽ join team `default`:

```python
init()  # Không có team parameter
# Returns: {"ok":1, ..., "team":"default"}
```

⚠️ **Warning**: Tất cả agents không chỉ định team đều vào `default` - có thể thấy broadcasts của nhau dù làm việc trên projects khác nhau!

### Team Isolation Architecture

```
~/.beads-village/
├── ecommerce/            # Team A
│   ├── mail/             # Team A broadcasts only
│   └── agents/           # Team A agent registry
├── internal-tools/       # Team B (completely isolated)
│   ├── mail/
│   └── agents/
└── default/              # Default team (all unassigned agents)
    ├── mail/
    └── agents/
```

### Scope Comparison

| Scope | Directory | Who Sees | Use Case |
|-------|-----------|----------|----------|
| **Local** | `/workspace/.mail/` | Only agents in THIS workspace | Workspace-specific coordination |
| **Team** | `~/.beads-village/{team}/mail/` | All agents in same team | Cross-workspace announcements |

### Common Team Patterns

#### Pattern 1: Single Project with Multiple Repos
```python
# All repos for same project share a team
init(team="project-alpha")  # Agent in /alpha-api
init(team="project-alpha")  # Agent in /alpha-web
init(team="project-alpha")  # Agent in /alpha-mobile
```

#### Pattern 2: Multiple Independent Projects
```python
# Each project is isolated
init(team="project-alpha")  # Alpha agents
init(team="project-beta")   # Beta agents (cannot see Alpha)
```

#### Pattern 3: Shared Library Development
```python
# Core team works on shared libs
init(team="platform-core")  # Agent in /shared-lib

# Consuming teams are separate
init(team="app-team-a")     # Agent in /app-a (isolated from core)
init(team="app-team-b")     # Agent in /app-b (isolated from core)
```

---

## 🔧 Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `workspace not found` | Invalid path in init() | Check path exists |
| `bd CLI not found` | Beads not installed | `go install github.com/steveyegge/beads/cmd/bd@latest` |
| `no ready tasks` | No claimable work | Use `add()` to create tasks or `ls()` to see all |
| `file reserved by agent-X` | Conflict | Wait, message agent, or work on different files |
| `timeout` | Slow git operation | Run `sync()` manually, check network |

### When Things Go Wrong
```python
# Check system health
doctor()

# Force sync with git
sync()

# Clean up old issues (if >200 open)
cleanup(days=2)

# Check messages for coordination issues
inbox(unread=True)
```

---

## ✅ Best Practices Checklist

### Before Starting
- [ ] Call `init()` first
- [ ] Check `inbox()` for updates from other agents
- [ ] Run `ready()` to see available tasks

### During Work
- [ ] Always `reserve()` before editing files
- [ ] Create issues for side-discoveries with `add(..., desc="...")`
- [ ] Keep reservations short (TTL 600s = 10 min default)
- [ ] Check `reservations()` before editing new files

### When Completing
- [ ] Use descriptive `msg` in `done()` - explain what was done
- [ ] `broadcast()` important completions to team
- [ ] Restart session after `done()` for clean state

### Maintenance (Every Few Days)
- [ ] Run `cleanup(days=2)` to remove old closed issues
- [ ] Run `doctor()` to fix any database issues
- [ ] Keep <200 open issues for performance

---

## 📝 Response Field Reference

| Field | Meaning | Example |
|-------|---------|---------|
| `id` | Issue ID | `"bd-42"` |
| `t` | Title | `"Fix auth bug"` |
| `p` | Priority | `1` (high) |
| `s` | Status | `"in_progress"` |
| `f` | From (sender) | `"agent-be"` |
| `b` | Body | `"Login API ready..."` |
| `ts` | Timestamp | `"2024-01-15T10:30:00"` |
| `ws` | Workspace | `"/projects/api"` |
| `team` | Team name | `"my-project"` |
| `global` | From team hub | `true` |
| `imp` | Importance | `"high"` |

---

## 🚀 Example Complete Session

```python
# === Starting a new work session ===
Agent: I'll initialize beads village and see what work is available.

init()
# {"ok":1, "agent":"agent-001", "ws":"C:\\project", "team":"default"}

inbox(unread=True)
# [{"f":"agent-002", "s":"Auth API Ready", "b":"POST /auth/login deployed", "global":true}]

Agent: I see the auth API is ready. Let me claim the next task.

claim()
# {"id":"bd-50", "t":"Add login form", "p":1, "s":"in_progress"}

Agent: Got the login form task. I'll reserve the files I need.

reserve(paths=["src/components/Login.tsx", "src/api/auth.ts"], reason="bd-50")
# {"granted":["src/components/Login.tsx","src/api/auth.ts"], "conflicts":[]}

Agent: Files reserved. Now implementing...
[implements login form]

Agent: While implementing, I noticed we need form validation. I'll file that.

add(
    title="Add form validation to login",
    desc="Need client-side validation for email format and password length. Found during bd-50.",
    typ="task",
    pri=2,
    parent="bd-50"
)
# {"id":"bd-51", "t":"Add form validation to login", "p":2}

Agent: Login form complete. Marking done and announcing to team.

done(id="bd-50", msg="Login form implemented using auth API. Filed bd-51 for validation.")
# {"ok":1, "done":1, "hint":"restart session for best performance"}

broadcast(subj="Login Form Ready", body="FE login at /login - uses POST /auth/login")
# {"sent":1, "global":true}

Agent: Task complete. Restarting session as recommended.
```
