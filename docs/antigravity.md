# 🚀 Antigravity CLI Integration Guide

This guide describes how `dev-mcp` is orchestrated and consumed by the **Antigravity CLI (agy)** host client designed by Google DeepMind.

---

## 🧭 1. Overview of Orchestration

Antigravity operates as the main user-facing CLI client. It runs autonomous development loops, reads project rules, and calls background MCP servers to execute steps.

```
                  Developer (CLI Terminal)
                             │
                             ▼
               Antigravity CLI Client (agy)
                ↙                         ↘
        dev-mcp Server             Open Design MCP
  (OS, State, Backlog, Git)      (Design-to-Code Render)
```

In this architecture:
- **`dev-mcp`** serves as the **Project brain & State Engine**. It keeps track of the context JSON, requirements backlog, safety configurations, milestones, and Git synchronization.
- **`agy`** acts as the agentic scheduler, coordinating code edits, verifying safety boundaries, and resolving dependencies.

---

## 🛠️ 2. Connecting dev-mcp to Antigravity

Antigravity executes MCP processes using standard pipe configurations.

### Configuration Template

To configure the Antigravity runtime to load `dev-mcp`, register the server in your `~/.gemini/antigravity-cli/mcp_config.json`:

**Option A: Installed CLI command (recommended)**
```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "dev-mcp",
      "env": {
        "DEV_MCP_PROFILE": "all"
      }
    }
  }
}
```

**Option B: Local source checkout**
```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "/path/to/dev-mcp/.venv/bin/python",
      "args": ["/path/to/dev-mcp/server.py"],
      "env": {
        "DEV_MCP_PROFILE": "all"
      }
    }
  }
}
```

---

## 💬 3. Standard Integration Commands

> **Important Architectural Distinction:** Slash commands (e.g., `/goal`, `/schedule`, `/grill-me`, `/teamwork`, `/learn`) are **host client features** provided by Google DeepMind's Antigravity CLI (`agy`), **not** native MCP tools implemented by `dev-mcp`. The `dev-mcp` server exposes **91 standard MCP tools across 18 modules** (such as `create_task`, `sync_workspace`, `verify_work`, `bootstrap_project`, `desktop_snapshot`), which the Antigravity agentic engine invokes autonomously to inspect, modify, and verify the workspace during these sessions.

When pair-programming with Antigravity, developers frequently use the following host slash commands:
- **`/goal`**: Start long-running, multi-step autonomous development cycles.
- **`/schedule`**: Set recurring schedules or cron timers for workspace health syncs.
- **`/grill-me`**: Interactively review requirements specifications and challenge architecture decisions.
- **`/teamwork-preview`**: Orchestrate multi-agent workflows and subagent task delegation.
- **`/learn`**: Extract and persist domain knowledge into repository or agent memory.
