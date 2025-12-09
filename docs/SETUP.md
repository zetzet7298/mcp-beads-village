# Installation & Setup Guide

Complete setup instructions for all supported AI coding agents and IDEs.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [IDE/Agent Configuration](#ideagent-configuration)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code (CLI)](#claude-code-cli)
  - [Cursor](#cursor)
  - [GitHub Copilot (VS Code)](#github-copilot-vs-code)
  - [Amp Code](#amp-code)
  - [Kilo Code](#kilo-code)
  - [Windsurf](#windsurf)
  - [OpenCode](#opencode)
  - [Cline](#cline)
  - [Roo Code](#roo-code)
  - [Zed Editor](#zed-editor)
  - [Continue](#continue)
  - [Aider](#aider)
- [Configuration Summary](#configuration-summary)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required: Install Beads CLI

```bash
# Install via pip
pip install beads

# Verify installation
bd --version
```

> ⚠️ **Important**: Without Beads CLI installed, the MCP server will not function properly.

### System Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| Node.js | 16+ (for npx) |
| Git | Latest |

---

## Installation

```bash
# Option 1: npx (recommended)
npx beads-village

# Option 2: npm global
npm install -g beads-village

# Option 3: pip
pip install beads-village
```

---

## IDE/Agent Configuration

### Claude Desktop

**Config file location:**
| OS | Path |
|----|------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

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

---

### Claude Code (CLI)

**Via CLI command:**

```bash
# Current project only
claude mcp add beads-village --scope local -- npx beads-village

# All projects (user scope)
claude mcp add beads-village --scope user -- npx beads-village

# Shared project config (.mcp.json)
claude mcp add beads-village --scope project -- npx beads-village
```

**Via `.mcp.json`** (project root):

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

| Scope | Description |
|-------|-------------|
| `local` | Only you, current project (default) |
| `project` | Shared via `.mcp.json` |
| `user` | All your projects |

---

### Cursor

**Method 1: Settings UI**

1. Open Settings (`Ctrl+,` / `Cmd+,`)
2. Search "MCP" → **Features > MCP Servers**
3. Click **Add Server**
4. Configure: Name=`beads-village`, Command=`npx`, Args=`beads-village`

**Method 2: Config file**

Create `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

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

---

### GitHub Copilot (VS Code)

**Via settings.json:**

```json
{
  "github.copilot.chat.mcp.servers": {
    "beads-village": {
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

**Via workspace** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "beads-village": {
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

> ⚠️ MCP in GitHub Copilot may require VS Code and admin policy enablement.

---

### Amp Code

**Via CLI:**

```bash
# Workspace
amp mcp add --workspace beads-village -- npx beads-village

# Global
amp mcp add beads-village -- npx beads-village
```

**Via config** (`.amp/settings.json` or `.vscode/settings.json`):

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

---

### Kilo Code

**Method 1: Settings UI**

1. `Ctrl+Shift+P` → "Kilo Code: Open Settings"
2. Navigate to **MCP Servers**
3. Add: Name=`beads-village`, Type=`stdio`, Command=`npx`, Args=`["beads-village"]`

**Method 2: settings.json**

```json
{
  "kilocode.mcpServers": {
    "beads-village": {
      "type": "stdio",
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

---

### Windsurf

Create `~/.windsurf/mcp.json` or project-level config:

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

---

### OpenCode

**Via CLI:**

```bash
# Add MCP server
opencode mcp add beads-village -- npx beads-village
```

**Via config** (`opencode.json` or `opencode.jsonc`):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcpServers": {
    "beads-village": {
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

**Config locations (order of precedence):**
1. `./opencode.json` (project)
2. `~/.config/opencode/config.json` (user)

> 📖 See [OpenCode MCP Docs](https://opencode.ai/docs/mcp-servers/) for advanced options.

---

### Cline

**Via Settings UI (recommended):**

1. Open VS Code → Cline extension
2. Click **MCP Servers** in Cline sidebar
3. Click **Configure MCP Servers**
4. Add configuration:

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

**Config location:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

> 📖 See [Cline MCP Docs](https://docs.cline.bot/mcp/configuring-mcp-servers) for details.

---

### Roo Code

**Via Settings UI:**

1. Open Roo Code settings in VS Code
2. Navigate to **MCP Servers** section
3. Add new server with STDIO transport

**Via config:**

```json
{
  "mcpServers": {
    "beads-village": {
      "transport": "stdio",
      "command": "npx",
      "args": ["beads-village"]
    }
  }
}
```

> 📖 See [Roo Code MCP Docs](https://docs.roocode.com/features/mcp/using-mcp-in-roo) for transport options.

---

### Zed Editor

**Via Settings:**

Open Zed settings (`Cmd+,`) and add to `context_servers`:

```json
{
  "context_servers": {
    "beads-village": {
      "command": {
        "path": "npx",
        "args": ["beads-village"]
      }
    }
  }
}
```

**Via Extension (if available):**

Check Zed Extensions for pre-built MCP server extensions.

> 📖 See [Zed MCP Docs](https://zed.dev/docs/ai/mcp) for more info.

---

### Continue

**Via config.yaml** (`~/.continue/config.yaml`):

```yaml
mcpServers:
  - name: beads-village
    command: npx
    args:
      - beads-village
```

**Via config.json** (legacy):

```json
{
  "mcpServers": [
    {
      "name": "beads-village",
      "command": "npx",
      "args": ["beads-village"]
    }
  ]
}
```

> 📖 See [Continue MCP Docs](https://docs.continue.dev/customize/deep-dives/mcp) for setup guide.

---

### Aider

Aider supports MCP through external tools like `aider-mcp-server` or `mcpm-aider`.

**Using mcpm (MCP Manager):**

```bash
# Install mcpm
pip install mcpm

# Add beads-village
mcpm add beads-village --command "npx beads-village"
```

**Using aider-mcp-server:**

```bash
# Install
pip install aider-mcp-server

# Configure in your MCP client to connect Aider
```

> 📖 See [Aider MCP Integration](https://github.com/disler/aider-mcp-server) for details.

---

## Configuration Summary

| Client | Config File | Config Key |
|--------|-------------|------------|
| Claude Desktop | `claude_desktop_config.json` | `mcpServers` |
| Claude Code | `.mcp.json` | `mcpServers` |
| Cursor | `.cursor/mcp.json` | `mcpServers` |
| GitHub Copilot | `settings.json` | `github.copilot.chat.mcp.servers` |
| Amp Code | `.amp/settings.json` | `amp.mcpServers` |
| Kilo Code | `settings.json` | `kilocode.mcpServers` |
| Windsurf | `~/.windsurf/mcp.json` | `mcpServers` |
| OpenCode | `opencode.json` | `mcpServers` |
| Cline | Cline settings | `mcpServers` |
| Roo Code | Roo settings | `mcpServers` |
| Zed | Zed settings | `context_servers` |
| Continue | `config.yaml` | `mcpServers` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `bd: command not found` | Install Beads CLI: `pip install beads` |
| MCP server not starting | Check Node.js 16+ installed |
| Tools not appearing | Restart IDE after config changes |
| Permission errors | Ensure write access to workspace |
| Connection timeout | Check `npx beads-village` runs manually |

### Verify Installation

```bash
# Check Beads CLI
bd --version

# Check Node.js
node --version

# Test MCP server
npx beads-village --help
```

---

[← Back to README](../README.md)
