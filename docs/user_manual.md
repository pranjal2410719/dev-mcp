# 🧠 dev-mcp: AI Engineering Operating System — User Manual & Developer Guide (v2.1.0)

Welcome to the official User Manual and Developer Guide for **`dev-mcp` (Version 2.1.0)**. This document serves as the comprehensive technical reference for installing, configuring, automating, and contributing to the `dev-mcp` Model Context Protocol (MCP) server.

---

## 👥 1. Author & Maintainer Profile

For issues, questions, or collaboration requests, contact:

* **Name:** Pranjal Yadav
* **Email:** [2k24.cs1l.2410719@gmail.com](mailto:2k24.cs1l.2410719@gmail.com)
* **Phone:** +91 9219920362
* **LinkedIn:** [linkedin.com/in/-pranjal22/](https://www.linkedin.com/in/-pranjal22/)
* **GitHub:** [github.com/pranjal2410719](https://github.com/pranjal2410719)

---

## 🚀 2. Full Setup & Installation Guide

### Prerequisites
- **Python 3.10+** (Required runtime).
- **Git** (Required for version control, commit automation, and workspace synchronization).
- **pip** or **uv** (Recommended Python package managers).
- *(Optional)* **agent-desktop** (`npm install -g agent-desktop`) for desktop GUI automation and AT-SPI accessibility tree inspection.
- *(Optional)* **ripgrep** (`sudo apt install ripgrep`) for accelerated code search.

### Local Installation
Navigate to your `dev-mcp` directory and set up a dedicated virtual environment:

```bash
# Navigate to the server repository
cd /path/to/dev-mcp

# Create a virtual environment using uv (recommended for speed)
uv venv
source .venv/bin/activate
uv pip install -e .

# OR using standard python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## ⚙️ 3. Configuring AI Clients (Cross-Platform)

Configure the server in your editor or assistant of choice. 

* **Absolute Command Path:** `/path/to/dev-mcp/.venv/bin/python`
* **Absolute Argument Path:** `/path/to/dev-mcp/server.py`

### Dynamic Tool Profiling (`DEV_MCP_PROFILE`)
To optimize LLM prompt token consumption, pass the `DEV_MCP_PROFILE` environment variable in your client configuration:
- `code`: Loads 10 modules (~4,200 tokens, **66.4% reduction**) — file ops, search, context, git ops, commands.
- `planning`: Loads PRD, todo engine, phases, context (~3,800 tokens, **69.6% reduction**).
- `audit`: Loads readiness, guardian, dependency, doctor, outcome (~4,500 tokens, **64.0% reduction**).
- `desktop`: Loads desktop ops, terminal, file ops (~3,100 tokens, **75.2% reduction**).
- `all` (default): Loads all 18 modules (84 tools).

### A. Claude Desktop
Add the configuration to:
* **Linux/macOS:** `~/.config/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

### B. Cursor
1. Go to **Settings** → **Features** → **MCP**.
2. Click **+ Add New MCP Server**.
3. Configure:
   - **Name:** `dev-mcp`
   - **Type:** `command`
   - **Command:** `/path/to/dev-mcp/.venv/bin/python /path/to/dev-mcp/server.py`
4. Click **Save**.

### C. Windsurf
1. Open **Settings** → **Advanced** → **MCP Configurations**.
2. Add the configuration:
```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "/path/to/dev-mcp/.venv/bin/python",
      "args": ["/path/to/dev-mcp/server.py"],
      "env": {
        "DEV_MCP_PROFILE": "code"
      }
    }
  }
}
```

### D. VS Code (Cline / Roo Code)
If using Cline, open extension settings, select **MCP Settings**, and add:
```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "/path/to/dev-mcp/.venv/bin/python",
      "args": ["/path/to/dev-mcp/server.py"]
    }
  }
}
```

---

## 🕹️ 4. Host Client Integration (Antigravity CLI)

### What is `antigravity-cli`?
`antigravity-cli` is an agentic command-line developer interface designed by Google DeepMind. It serves as an **AI Agent host client** which spawns `dev-mcp` as a background stdio process. The agent communicates with `dev-mcp` to read context, plan sprints, manage tasks, and run PM audits.

### Built-in CLI Slash Commands
When executing inside `antigravity-cli`, developers have access to direct slash commands:

* **`/goal`** — Instructs the agent to run an autonomous, long-running cycle (e.g. overnight execution) that continues until the goal is fully achieved.
* **`/schedule`** — Configures automated timer reminders or recurring cron schedules (e.g., `*/5 * * * *` to run workspace syncs every 5 minutes).
* **`/grill-me`** — Starts an interactive interview between the agent and developer to clarify goals and draft technical specifications.
* **`/teamwork`** — Coordinates a swarm of autonomous subagents.
* **`/learn`** — Directs the agent to persist corrections or custom setup workflows across subsequent workspace sessions.

---

## 🕹️ 4.1 Interactive Keyboard Shortcut Guide (`dev-mcp-guide`)

`dev-mcp` includes a built-in terminal-based interactive help guide:
```bash
dev-mcp-guide
```
Alternatively, when running `dev-mcp` interactively in a terminal, press `?`, `h`, or `/` to temporarily display this guide.

### Guide Navigation Shortcuts:
- **← / →** or **Tab**: Cycle between tabs (General, Commands, Shortcuts).
- **↑ / ↓**: Scroll within the active tab.
- **esc / q**: Exit and return back to the server process.

---

## 🔒 4.2 AI Engineering OS Security & Multi-Agent Workspaces

`dev-mcp` v2.1.0 maintains a multi-tiered security model:

### 1. Workspace Lock
All file read/write operations and terminal command executions are jailed inside the active project root directory when `safety_mode` is `safe` or `trusted`. Traversal escapes (`..` or writing to system folders) raise a `PermissionError`.

### 2. High-Performance Path Validation
In v2.1.0, `security.py` eliminates slow stack-inspection calls on standard paths, making path validation **26.2× faster** (0.087ms vs 2.28ms).

### 3. Safety Modes
Configurations inside `.project_brain/config.yaml` define safety bounds:
- **`safe`** (default): Restricts modifications to project root, blocks destructive shell commands (`sudo`, `reboot`, `rm -rf`, `git reset --hard`), blocks recursive file cleanups (`delete_recursive`).
- **`trusted`**: Limits execution to project root, but permits folder deletions and standard Git branch checkouts.
- **`lab`**: Disables workspace locks and command block lists (recommended only in throwaway VM containers).

---

## 👑 5. The Onboarding & Execution Workflow

`dev-mcp` operates around a linear project lifecycle:

```text
                         assess_project_readiness()
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼ (If score < 80, empty)                ▼ (If score < 80, legacy)
         bootstrap_project()                     adopt_existing_project()
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                                doctor() (diagnostics)
                                     │
                                     ▼
                                start_session()
                                     │
                                     ▼
                                project_dashboard()
                                     │
                                     ▼
                                next_best_action()
                                     │
                                     ▼
        [Sync Plan] ──►       sync_workspace()
                                     │
                                     ▼
        [Audit Code] ──►        verify_work()
                                     │
                                     ▼
        [GUI Verification] ──► desktop_verify_element()
                                     │
                                     ▼
        [Audit Goal] ──►       verify_outcome()
                                     │
                                     ▼
                                end_session()
                                     │
                                     ▼
                          prepare_commit() ──► commit_changes()
```

---

## 🛠️ 6. Complete MCP Tool Reference (84 Tools)

### A. Core Workspace Onboarding & Diagnostics (`brain/project_readiness.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `assess_project_readiness` | `path: str = "."` | Scan directory files and compute readiness score (0-100%) and maturity level (Levels 0-5). |
| `project_readiness_report` | `path: str = "."` | Generate a detailed Markdown checklist report of missing files, scoring audits, and recommendations. |
| `bootstrap_project` | `path: str = "."` | Generate empty template folders, configuration YAML, and context JSONs to onboard a fresh directory. |
| `adopt_existing_project` | `path: str = "."` | Scan an existing legacy repository (README, dependencies, structure) and draft initial context, PRD, and audit tasks. |
| `doctor` | `path: str = "."` | Audit setup integrity across 7 checklist layers (server, context file, brain folders, git, PRD, requirements JSON, active tasks). |
| `reset_project_brain` | `path: str = "."` | Wipe all project context metadata and Project Brain configs from a folder, leaving code and git untouched. |
| `archive_project_brain` | `path: str = "."` | Package Project Brain configurations to timestamped archives under `.project_brain_archive/` to allow pivots. |
| `create_project_workspace` | `name: str`, `template: str = "blank"`, `path: str = "."` | Create an isolated sibling workspace directory, initialize git, and bootstrap Project Brain. |

### B. Session Orchestration (`brain/orchestrator.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_project_brain` | `path: str = "."` | Aggregate active/completed tasks, git logs, and milestone progress into a consolidated dashboard. |
| `next_best_action` | `path: str = "."` | Recommend the highest priority task to execute next based on phase, dependencies, and priorities. |
| `start_session` | `path: str = "."` | Start a development session and generate a markdown sprint brief detailing goals and handoffs. |
| `end_session` | `session_summary: str`, `known_issues: str = ""`, `path: str = "."` | Terminate sprint session, record progress, and output handoff files. |
| `prepare_commit` | `session_summary: str`, `path: str = "."` | Analyze modified/untracked files and generate suggested conventional git commit messages. |
| `commit_changes` | `message: str`, `path: str = "."` | Stage all files (`git add .`) and commit with the approved message. |

### C. Task & Todo Engine (`brain/todo_engine.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `create_task` | `title: str`, `description: str`, `phase: str = ""`, `priority: str = "medium"`, `depends_on: str = ""`, `path: str = "."` | Create a new task entry with priorities, phase limits, and dependency chains. |
| `update_task` | `task_id: str`, `status: str = ""`, `priority: str = ""`, `title: str = ""`, `path: str = "."` | Update status, priority, or title of a specific task. |
| `complete_task` | `task_id: str`, `notes: str = ""`, `path: str = "."` | Close a task, logging notes and moving it to completed records. |
| `next_task` | `path: str = "."` | Extract the highest priority task ready for development. |
| `blocked_tasks` | `path: str = "."` | List all tasks blocked by unmet dependency tasks. |
| `list_tasks` | `phase: str = ""`, `status: str = ""`, `priority: str = ""`, `path: str = "."` | Retrieve all registered tasks, optionally filtered by status, phase, or priority. |

### D. Phase & Milestone Management (`brain/phase_manager.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_current_phase` | `path: str = "."` | Get the currently active development phase and status details. |
| `set_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Set the active phase. Only tasks in this phase are considered in scope. |
| `complete_phase` | `notes: str = ""`, `path: str = "."` | Mark current phase as completed and advance milestone progress. |
| `next_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Conclude the current phase and advance directly to the next phase. |
| `list_phases` | `path: str = "."` | Display a list of all defined phases and their statuses. |
| `add_milestone` | `name: str`, `target_date: str = ""`, `features: str = ""`, `path: str = "."` | Define a new project milestone tracking key features. |
| `list_milestones` | `path: str = "."` | Display all milestones and target completion dates. |

### E. PRD & Requirements Traceability (`brain/prd_manager.py`, `brain/requirements.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_prd` | `document: str = "PRD"`, `path: str = "."` | Retrieve markdown PRD document contents (PRD, VISION, SCOPE, REQUIREMENTS). |
| `update_prd` | `document: str`, `content: str`, `path: str = "."` | Write or update target specification markdown files. |
| `summarize_prd` | `path: str = "."` | Extract concise bulleted requirement summaries from all specifications. |
| `compare_work_to_prd` | `path: str = "."` | Audit task backlogs and contexts against the PRD to detect alignment gaps. |
| `extract_requirements` | `path: str = "."` | Extract structured requirement tags and keywords from the PRD markdown into `requirements.json`. |
| `verify_requirements` | `feature_name: str = ""`, `path: str = "."` | Scan codebase files to map requirement status based on keyword density. |
| `verify_outcome` | `task_id: str`, `path: str = "."` | Verify user entrypoints, validations, persistence schemas, and error pathways for a target task. |

### F. Workspace Sync & Reality Checks (`brain/sync_engine.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `sync_workspace` | `path: str = "."` | Match Git branches, commits, and diff structures to the backlog to auto-detect finished work. |
| `verify_work` | `task_id: str`, `path: str = "."` | Compile verification confidence reports using tests, Git status, and guardian audits. |
| `project_dashboard` | `path: str = "."` | Generate a unified dashboard displaying workspace git states, tasks, phases, and overall health scores. |

### G. Sprint Handoffs (`brain/handoff_engine.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_handoff` | `session_summary: str = ""`, `known_issues: str = ""`, `path: str = "."` | Save the current session log to `.project_brain/handoffs/`. |
| `get_last_handoff` | `path: str = "."` | Load the most recently saved handoff file to restore AI state across sessions. |
| `list_handoffs` | `path: str = "."` | Display a list of all historical handoff logs. |

### H. Architecture & Dependency Control (`brain/guardian.py`, `brain/dependency.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `validate_architecture` | `path: str = "."` | Scan codebase imports against the forbidden and required technologies list. |
| `build_dependency_graph` | `path: str = "."` | Parse imports to build a complete connection graph with cached AST parsing. |
| `impact_analysis` | `file_path: str`, `path: str = "."` | Perform a BFS traversal of dependencies to calculate the blast radius of a modified module. |

### I. Project Context CRUD (`tools/context_mgmt.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `init_context` | `path: str = "."` | Scans workspace config files to initialize a project context metadata file. |
| `get_context` | `dot_path: str = ""`, `path: str = "."` | Retrieve a field value from context JSON using dot path lookups (e.g. `tech_stack.languages`). |
| `update_context` | `dot_path: str`, `value: str`, `path: str = "."` | Set or update a value in the context JSON. |
| `add_to_context_list` | `dot_path: str`, `item: str`, `path: str = "."` | Append strings or JSON objects to list fields in context. |
| `add_key_file` | `file_path: str`, `purpose: str`, `details: str = ""`, `root_path: str = "."` | Track critical codebase files and their architectural role. |
| `add_task` | `task_id: str`, `description: str`, `status: str = "pending"`, `branch: str = ""`, `notes: str = ""`, `path: str = "."` | Direct insert of active tasks into context records. |
| `add_decision` | `decision: str`, `reason: str`, `alternatives: str = ""`, `path: str = "."` | Log Architecture Decision Records (ADRs) to track project constraints. |
| `export_context_markdown` | `path: str = "."` | Export project context metadata to `.project-context.md` for external sharing. |
| `remove_context_item` | `dot_path: str`, `index: int`, `path: str = "."` | Remove list elements by index from context list fields. |
| `reset_context` | `path: str = "."` | Revert `.project-context.json` fields to defaults. |
| `project_info` | `path: str = "."` | Count files and directories, checking project runtime types. |

### J. High-Performance Sandboxed File Operations (`tools/file_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `read_file` | `path: str`, `start_line: int = None`, `end_line: int = None`, `line_numbers: bool = False` | Read files with line-slicing, numbering, and >2500 line safety truncation guard. |
| `write_file` | `path: str`, `content: str`, `append: bool = False` | Atomic write using temporary files and `os.replace` with directory auto-creation. |
| `edit_file` | `path: str`, `old_string: str`, `new_string: str`, `count: int = None` | In-place replacement with exact count control and whitespace mismatch hints. |
| `batch_replace` | `file_paths: list[str]`, `old_string: str`, `new_string: str` | Atomic multi-file text replacement in a single operation. |
| `file_info` | `path: str` | Retrieve file size, line count, modified time, and permissions. |
| `delete_path` | `path: str` | Delete a single file or empty folder. |
| `delete_recursive` | `path: str` | Recursively delete folder trees (blocked in `safe` mode). |
| `list_directory` | `path: str` | List directory contents with human-readable file sizes and noise exclusion. |
| `glob_files` | `pattern: str`, `base_path: str = "."` | Retrieve paths matching globs with noise filtering (`.git`, `node_modules`, etc.). |
| `create_directory` | `path: str` | Create missing directory paths (`mkdir -p`). |

### K. Terminal, Git & Code Search Helpers (`tools/terminal.py`, `tools/search.py`, `tools/git_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `run_command` | `command: str`, `timeout_seconds: int = 60`, `workdir: str = None` | Execute shell commands inside authorized directory under strict timeouts. |
| `search_code` | `pattern: str`, `path: str = "."`, `glob_filter: str = None`, `max_results: int = 50`, `context_lines: int = 0` | High-speed search using Ripgrep (`rg`) with Python fallback and context lines. |
| `git_status` | `repo_path: str = "."` | Print directory version status (`git status`). |
| `git_diff` | `repo_path: str = "."`, `staged: bool = False` | Return staged or unstaged modifications. |
| `git_log` | `repo_path: str = "."`, `max_count: int = 10` | Print recent commits. |
| `git_branch` | `repo_path: str = "."` | List local branches. |
| `git_add` | `repo_path: str = "."`, `files: str = "."` | Stage target modified files. |
| `git_commit` | `repo_path: str = "."`, `message: str = "update"` | Commit changes using Conventional Commits rules. |
| `git_create_branch` | `repo_path: str = "."`, `branch_name: str = ""` | Create and switch checkout branches. |
| `install_git_hooks` | `repo_path: str = "."` | Install Git pre-commit hook to auto-sync `.project_brain` on every native commit. |

### L. Desktop GUI Automation & Inspection (`tools/desktop_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `desktop_status` | None | Verify `agent-desktop` CLI installation and OS accessibility permissions. |
| `desktop_list_apps` | None | List running applications with process names and window titles. |
| `desktop_list_windows` | None | Enumerate active desktop windows and their bounds. |
| `desktop_snapshot` | `app: str = ""` | Capture hierarchical accessibility tree state (JSON/YAML). |
| `desktop_find` | `name: str = ""`, `role: str = ""`, `app: str = ""` | Query specific UI nodes (buttons, inputs, menus) in the UI tree. |
| `desktop_click` | `name: str = ""`, `role: str = ""`, `app: str = ""` | Simulate native mouse click on target desktop element. |
| `desktop_type` | `text: str`, `app: str = ""` | Send native keyboard keystrokes to active window. |
| `desktop_verify_element` | `name: str`, `role: str = ""`, `app: str = ""` | Assert that an expected element exists and is visible on desktop. |
| `desktop_screenshot` | `output_path: str = "screenshot.png"` | Capture high-resolution desktop display screenshot. |

### M. Server Profiling (`server.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_dev_mcp_profile` | None | Query active profile mode, loaded module count, and active tools. |

---

## 🧩 7. Prompts & Resources Reference

### Prompts
1. **`project-overview`** — Injects the entire project context JSON in markdown format, outputting development guidelines for the model.
2. **`code-review`** — Loads project conventions and tech stack to provide specific checklists for reviewing code.
3. **`architectural-decision`** — Provides a structured markdown template to record Architecture Decision Records (ADRs).
4. **`feature-plan`** — Generates a blueprint template for planning branches, milestones, tasks, and target files.

### Resources
1. **`project://context/json`** — Returns `.project-context.json` content as JSON.
2. **`project://context/markdown`** — Returns `.project-context.json` context parsed as a Markdown layout.

---

## ⚙️ 8. Workspace Configuration (`.project_brain/config.yaml`)

Each project generates a local YAML configuration for customization:

```yaml
project_type: auto          # 'auto' or 'legacy'
language: auto              # Primary codebase language
framework: auto             # Primary web framework
readiness_threshold: 80     # Score threshold to begin tasks
verification_threshold: 85  # Verification confidence to autocomplete
auto_sync: true             # Automatically parse changes in dashboard
safety_mode: safe           # 'safe', 'trusted', or 'lab'
```

---

## 🔒 9. Security Sandbox & Safety Modes

All operations in `dev-mcp` v2.1.0 are governed by a multi-tiered security architecture:

### 1. Workspace Lock (Jailing)
In **`safe`** and **`trusted`** modes, all file tool operations and terminal working directories are jailed to the active project root directory. Any attempt to traverse parent directories (via `..`) or access external absolute paths raises a `PermissionError`.

### 2. Fast Path Validation
Path resolution checks root containment directly without invoking stack inspection on normal paths. When outside root, stack inspection permits onboarding operations (`bootstrap_project`, `create_project_workspace`, `adopt_existing_project`, `init_context`).

### 3. Safety Modes
- **`safe` (Default):** Workspace Lock active. Destructive terminal commands (`sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `rm -rf`, `git reset --hard`, `git clean -fd`) and recursive deletions (`delete_recursive`) are blocked.
- **`trusted`:** Workspace Lock active. System-level commands remain blocked, but workspace cleanup (`rm -rf`, `delete_recursive`) and git branch/checkout operations are permitted within the project root.
- **`lab`:** Workspace Lock disabled. Allows arbitrary actions, falling back to an allowed directory allowlist (CWD, `DEV_MCP_ALLOWED_DIRS`, and `$HOME`).

---

## 🔌 10. Troubleshooting & Connection Lifecycle

- **Stateful Connection:** AI clients cache the active `stdio` pipe connection to the server process.
- **Out-of-Sync State:** If the server is updated or restarted, the client’s stdio connection can become stale, resulting in `EOF` or `client closing` errors.
- **Project Switching (No Context Leakage):** The global context cache in [app.py](../app.py) checks if the target root is different from the cached path during tool execution (`_root != target_root`), preventing tasks and metadata from leaking across projects.

### How to Reconnect Across Clients:
* **Cursor:** Go to **Settings** → **Features** → **MCP** → find `dev-mcp` and click **Restart**.
* **Claude Desktop:** Fully **Quit** the app from your taskbar/dock and reopen it to force Claude to spawn a new MCP process.
* **Cline / Roo Code:** Restart the extension or trigger a reconnect via `/mcp restart dev-mcp`.
* **Windsurf:** Reload the editor window or restart the workspace connection.

---

## 🧪 11. Running Validation Tests

```bash
# Run all unit and optimization test suites
.venv/bin/python -m unittest discover -s tests -p "*.py" -v

# Run the end-to-end MCP workflow verification
.venv/bin/python tests/validate_mcp_flow.py

# Run optimization benchmarks
.venv/bin/python tests/test_optimizations.py
```
