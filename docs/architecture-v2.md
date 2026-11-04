# 🏗️ Architecture Design — dev-mcp v2.0.0 (AI Engineering OS)

This document describes the architectural layout, modules, and execution boundaries of **`dev-mcp` v2.0.0**, highlighting how it orchestrates multi-agent environments, jailing constraints, and metadata flows.

---

## 🗺️ 1. Orchestration Topology

`dev-mcp` v2.0.0 transitions from a standalone context tool to the stateful engine of a larger **AI Engineering OS** ecosystem. It is coordinated alongside design render systems (Open Design) by a parent client runner (such as Google DeepMind's Antigravity).

```text
                  Developer (CLI Terminal)
                             │
                             ▼
               Antigravity CLI Client (agy)
                 /                       \
                ▼                         ▼
         dev-mcp Server             Open Design MCP
  (OS, State, Backlog, Git)      (Design-to-Code Render)
                \                         /
                 ▼                       ▼
                     Project Workspace
                             │
                             ▼
                       Project Brain
```

---

## 📦 2. Sibling Directory & Isolation Layout

To support multiple AI-driven project developments concurrently, `dev-mcp` isolates context files and backlog history using sibling project root folders:

```text
/projects-dir/
├── dev-mcp/                     # Central tool server package
├── open-design/                 # Design render engine package
└── workspaces/                  # User workspace root
    ├── app-dashboard/           # Next.js workspace
    │   ├── .project-context.json
    │   └── .project_brain/
    └── python-utility/          # Python CLI workspace
        ├── .project-context.json
        └── .project_brain/
```

- Each project workspace contains a self-contained **Project Brain** (`.project_brain/`) and a central context record (`.project-context.json`).
- Path validation checks and command runners are dynamically jailed inside the active project directory, preventing cross-workspace context leakage.

---

## 🔒 3. Workspace Lock & Safety Guardrails

Security is enforced at the server's lowest validation layers to prevent destructive commands or arbitrary file operations:

```text
[ LLM Code Generation / Command Tool Invocation ]
                       │
                       ▼
         validate_path() / Command Check
                       │
             safety_mode configured?
             /         │          \
            ▼          ▼           ▼
        ("safe")   ("trusted")   ("lab")
           │           │           │
           │      Workspace Lock   │
    Workspace Lock     Active      │
    Destructive Block  No Sys Cmds │
           │           │           │
           ▼           ▼           ▼
      [Execute]    [Execute]   [Execute]
```

### Safety Constraints Matrix
1. **Workspace Lock**: In `safe` and `trusted` modes, paths are checked via `Path.relative_to(root)`. If a path escapes the root directory, a `PermissionError` is raised.
2. **Command Blocklist**: Heavy regex audits filter command execution to reject relative traversal (`..`), system dangerous utilities (`sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0`), and user absolute paths outside the workspace (except system directories: `/bin`, `/usr/bin`, `/usr/lib`, `/lib`, `/etc/alternatives`, `/etc/ssl`).
3. **Safe mode specific**: Blocks recursive deletion (`delete_recursive`), hard git resets (`git reset --hard`), and untracked cleans (`git clean -fd`).
4. **Stack Inspection Bypass**: Python call-stack inspection (`inspect.stack()`) allows onboarding tools (`bootstrap_project`, `create_project_workspace`, and `adopt_existing_project`) to operate on parent and sibling directories outside the current workspace lock.

---

## ⚙️ 4. Server Runtime & Registered Capabilities

- **Runtime**: FastMCP 3.4.2 application initialized in `app.py`.
- **Dual-Mode Entrypoint (`server.py`)**:
  - **Pipe Mode** (`not sys.stdin.isatty()`): Standard stdio JSON-RPC transport for MCP host clients (Antigravity, Cursor, Claude Desktop, Windsurf, Cline).
  - **TTY Mode** (`sys.stdin.isatty()`): Starts FastMCP server in a background daemon thread, displays a Rich ASCII banner, and monitors `/dev/tty` for interactive shortcuts (`?`, `h`, `/` to launch the `cli.py` reference guide; `q`, `ESC` to quit).
- **Capability Inventory (v2.0.0)**:
  - **71 Registered Tools**: 28 tools across 5 tool modules (`file_ops`, `search`, `terminal`, `git_ops`, `context_mgmt`) and 43 tools across 10 brain modules (`prd_manager`, `phase_manager`, `todo_engine`, `handoff_engine`, `orchestrator`, `guardian`, `dependency`, `sync_engine`, `requirements`, `project_readiness`).
  - **2 Registered Resources**: `project://context/json` and `project://context/markdown`.
  - **4 Registered Prompts**: `project-overview`, `code-review`, `architectural-decision`, and `feature-plan`.
- **Project Brain Architecture**: Stateful persistence layer backed by `.project-context.json` and `.project_brain/` (containing `config.yaml`, PRD markdown files, structured `requirements.json`, `phases/`, `todos/`, and `handoffs/`). State is dynamically loaded and isolated per workspace via `app.load_context()`.
