# 🏗️ Architecture Design — dev-mcp v2.1.0 (AI Engineering OS)

This document describes the architectural layout, modules, and execution boundaries of **`dev-mcp` v2.1.0**, highlighting how it orchestrates multi-agent environments, jailing constraints, desktop automation, dynamic tool profiling, and persistent metadata flows.

---

## 🗺️ 1. Orchestration Topology & Execution Boundaries

`dev-mcp` v2.1.0 acts as the stateful engine and tool provider of an **AI Engineering OS** ecosystem. It bridges AI host coding clients with workspace persistence, source control, and desktop application verification:

```text
                  Developer / AI Host Client
      (Antigravity CLI, Cursor, Claude Desktop, Windsurf, Cline)
                             │
                             ▼
                dev-mcp Server (FastMCP 3.4.2)
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
Project Brain Layer      Tools Layer           Desktop Suite
(.project_brain/ &       (Files, Git,          (agent-desktop CLI,
 .project-context.json)   Terminal, Search)     AT-SPI Accessibility)
     │                       │                       │
     └───────────────────────┼───────────────────────┘
                             ▼
                 Project Workspace Sandbox
               (Path Jailing / Safety Modes)
```

### Boundary Separation: Host Client vs. Dev MCP
- **Host Client (e.g., Antigravity CLI, Cursor, Claude Code, Cline)**: Responsible for LLM reasoning, conversational turns, agentic scheduling loops, and host slash commands (e.g. `/goal`, `/schedule`, `/grill-me`, `/teamwork`, `/learn`).
- **Dev MCP Server**: Deterministic MCP server providing persistent state management (`.project_brain/`), 91 registered MCP tools across 18 modules, path jailing, and desktop GUI verification. Dev MCP does not execute slash commands directly; host agents invoke its tools via standard MCP JSON-RPC protocol.

---

## 📦 2. Sibling Directory & Multi-Workspace Isolation

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

Security is enforced at the server's lowest validation layers (`security.py`) to prevent destructive commands or arbitrary file operations:

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
5. **Guardrail vs. Process Isolation**: Safety modes enforce application-layer guardrails. For untrusted code execution, `dev-mcp` should be run inside containerized/VM sandboxes (Docker, gVisor, Podman). In `lab` mode, the workspace lock and command filters are disabled for power users; `lab` mode must always be container-isolated.
6. **Environment & Secrets**: Commands execute in the ambient process environment (`os.environ`). Standard outputs are not automatically scrubbed for secrets; credentials should not be exposed in command arguments.

---

## 🎯 4. Tool Profiling & Optimization Architecture (`DEV_MCP_PROFILE`)

In v2.1.0, `dev-mcp` implements dynamic tool profiling via `DEV_MCP_PROFILE` to reduce LLM system prompt token overhead:

| Profile | Token Overhead | Reduction | Modules Loaded | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `code` | ~4,200 tokens | **66.4%** | File Ops, Search, Context, Git Ops, Terminal | Fast daily coding and refactoring sprints |
| `planning` | ~3,800 tokens | **69.6%** | PRD Manager, Todo Engine, Phase Manager, Context | Technical project management and roadmaps |
| `audit` | ~4,500 tokens | **64.0%** | Readiness, Guardian, Dependency, Doctor, Outcome | Architecture review and security audits |
| `desktop` | ~3,600 tokens | **71.2%** | Desktop Ops, Terminal, File Ops | GUI testing and desktop automation |
| `all` (default) | ~12,500 tokens | 0% | All 18 modules (91 tools) | Full autonomous development workflows |

---

## 🖥️ 5. Desktop Automation Layer (`tools/desktop_ops.py`)

Dev MCP extends AI agent capabilities beyond source code into live operating system verification:
- **Transport**: Bridges with the `agent-desktop` CLI via standard process invocation.
- **Accessibility Tree**: Discovers interactive UI nodes via Linux AT-SPI, macOS AX, and Windows UI Automation.
- **Verification**: `desktop_verify_element` allows AI agents to assert UI state after running frontend builds.
- **Universal Action**: `desktop_action` exposes all 50+ actions of the underlying desktop engine.

---

## ⚙️ 6. Server Runtime & Registered Capabilities

- **Runtime**: FastMCP 3.4.2 application initialized in `app.py`.
- **Dual-Mode Entrypoint (`server.py`)**:
  - **Pipe Mode** (`not sys.stdin.isatty()`): Standard stdio JSON-RPC transport for MCP host clients (Antigravity, Cursor, Claude Desktop, Windsurf, Cline).
  - **TTY Mode** (`sys.stdin.isatty()`): Starts FastMCP server in a background daemon thread, displays a Rich ASCII banner, and monitors `/dev/tty` for interactive shortcuts (`?`, `h`, `/` to launch the `cli.py` reference guide; `q`, `ESC` to quit).
- **Capability Inventory (v2.1.0)**:
  - **91 Registered Tools across 18 specialized modules**:
    - **48 Tools in Tools Layer (7 modules)**: `file_ops` (10 tools), `search` (1 tool), `terminal` (1 tool), `git_ops` (8 tools), `context_mgmt` (11 tools), `desktop_ops` (16 tools), `profile` (1 tool).
    - **43 Tools in Brain Layer (10 modules)**: `prd_manager` (4 tools), `phase_manager` (7 tools), `todo_engine` (6 tools), `handoff_engine` (3 tools), `orchestrator` (6 tools), `guardian` (1 tool), `dependency` (2 tools), `sync_engine` (3 tools), `requirements` (3 tools), `project_readiness` (8 tools).
  - **2 Registered Resources**: `project://context/json` and `project://context/markdown`.
  - **4 Registered Prompts**: `project-overview`, `code-review`, `architectural-decision`, and `feature-plan`.
- **Project Brain Architecture**: Stateful persistence layer backed by `.project-context.json` and `.project_brain/` (containing `config.yaml`, PRD markdown files, structured `requirements.json`, `phases/`, `todos/`, and `handoffs/`). State is dynamically loaded and isolated per workspace via `app.load_context()`.

---

## 🔍 7. Verification & Readiness Semantics

- **Readiness Score (`assess_project_readiness`)**: A structural audit evaluating repository onboarding readiness (PRDs, requirements, git status, task definitions, and test scaffold existence) for AI agents, rather than deep static code debt analysis.
- **Workspace Sync (`sync_workspace`)**: Employs heuristic alignment (branch names, commit messages, and touched file paths) to suggest task completion status with confidence metrics.
- **Requirement Verification (`verify_requirements`)**: Maps PRD functional requirements to source code files using lexical extraction and keyword alignment. Complete verification requires paired test suite execution via `verify_work`.
