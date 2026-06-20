# 🧠 dev-mcp: AI Engineering Operating System — User Manual & Developer Guide

Welcome to the official User Manual and Developer Guide for **`dev-mcp` (Version 0.1.0)**. This document is a comprehensive guide to understanding, configuring, executing, and contributing to the `dev-mcp` Model Context Protocol (MCP) server.

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
- **Git** (Required for the `git_ops`, `sync_engine`, and commit automation).
- **pip** or **uv** (Recommended Python package managers).

### Local Installation
Navigate to your `dev-mcp` directory and set up a virtual environment:

```bash
# Navigate to the server directory
cd /home/dev/Desktop/projects/mcp/dev-mcp

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

Add the server command below to your editor of choice. 

* **Absolute Command Path:** `/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python`
* **Absolute Argument Path:** `/home/dev/Desktop/projects/mcp/dev-mcp/server.py`

### A. Claude Desktop
Add the configuration to:
* **Linux/macOS:** `~/.config/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python",
      "args": ["/home/dev/Desktop/projects/mcp/dev-mcp/server.py"]
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
   - **Command:** `/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python /home/dev/Desktop/projects/mcp/dev-mcp/server.py`
4. Click **Save**.

### C. Windsurf
1. Open **Settings** → **Advanced** → **MCP Configurations**.
2. Add the configuration:
```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python",
      "args": ["/home/dev/Desktop/projects/mcp/dev-mcp/server.py"]
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
      "command": "/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python",
      "args": ["/home/dev/Desktop/projects/mcp/dev-mcp/server.py"]
    }
  }
}
```

---

## 🕹️ 4. Host Client Integration (Antigravity CLI)

### What is `antigravity-cli`?
`antigravity-cli` is an agentic command-line developer interface designed by Google DeepMind. It serves as the **AI Agent host client** which spawns the `dev-mcp` server as a background stdio process. The agent communicates with `dev-mcp` to read context and perform PM audits.

### Built-in CLI Slash Commands
When executing inside `antigravity-cli`, developers have access to the following direct slash commands:

* **`/goal`** — Instructs the agent to run an autonomous, long-running cycle (e.g. overnight execution) that continues until the goal is fully achieved.
* **`/schedule`** — Configures automated timer reminders or recurring cron schedules (e.g., `*/5 * * * *` to run workspace syncs every 5 minutes).
* **`/grill-me`** — Starts an interactive interview between the agent and developer to clarify goals and draft technical specifications.
* **`/teamwork-preview`** — Boots the team coordination preview mode to coordinate a swarm of autonomous subagents.
* **`/learn`** — Directs the agent to persist corrections or custom setup workflows across subsequent workspace sessions.

---

## 🕹️ 4.1 Interactive Keyboard Shortcut Guide (`dev-mcp-guide`)

`dev-mcp` includes a built-in terminal-based interactive help guide. You can launch it directly in a shell using:
```bash
dev-mcp-guide
```
Alternatively, when running the `dev-mcp` server interactively in a terminal, press `?`, `h`, or `/` to temporarily suspend/overlay this guide directly from the running server process!

The interface is tab-navigable using **Rich** layout panel controls:
- **General**: Provides transport details, setup instructions, and quick configuration snippets for Claude Desktop, Cursor, and Windsurf.
- **Commands**: Displays a structured list of all 70 MCP tools with detailed categorizations.
- **Shortcuts**: Lists keyboard shortcut layouts for navigation, code editing, and dev-mcp specific tasks.

### Guide Navigation Shortcuts:
- **← / →** or **Tab**: Cycle between tabs.
- **↑ / ↓**: Scroll within the active tab.
- **esc / q**: Exit and return back to the server process.

---

## 👑 5. The Onboarding & Execution Workflow

`dev-mcp` operates around a linear project lifecycle, structured to prevent ad-hoc actions and ensure strict progress tracking:

```
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
        [Audit Goal] ──►       verify_outcome()
                                     │
                                     ▼
                                end_session()
                                     │
                                     ▼
                          prepare_commit() ──► commit_changes()
```

---

## 🛠️ 6. Complete MCP Tool Reference (70 Tools)

### A. Core Workspace Onboarding & Diagnostics
Located in `brain/project_readiness.py`. These tools evaluate codebase maturity and initialize metadata context structures.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `assess_project_readiness` | `path: str = "."` | Scan directory files and compute readiness score (0-100%) and maturity level (Levels 0-5). |
| `project_readiness_report` | `path: str = "."` | Generate a detailed Markdown checklist report of missing files, scoring audits, and recommendations. |
| `bootstrap_project` | `path: str = "."` | Generate empty template folders, configuration YAML, and context JSONs to onboard a fresh directory. |
| `adopt_existing_project` | `path: str = "."` | Scan an existing legacy repository (README, dependencies, structure) and draft initial context, PRD, and audit tasks. |
| `doctor` | `path: str = "."` | Audit setup integrity across 7 checklist layers (server, context file, brain folders, git, PRD, requirements JSON, active tasks). |
| `reset_project_brain` | `path: str = "."` | Wipe all project context metadata and Project Brain configs from a folder, leaving code and git histories untouched. |
| `archive_project_brain` | `path: str = "."` | Package Project Brain configurations to timestamped archives under `.project_brain_archive/` to allow pivots. |

### B. Session Orchestration
Located in `brain/orchestrator.py`. These tools control sprint sessions and commit code.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_project_brain` | `path: str = "."` | Aggregate active/completed tasks, git logs, and milestone progress into a consolidated dashboard JSON. |
| `next_best_action` | `path: str = "."` | Recommend the highest priority task to execute next based on branch names, dependencies, and priorities. |
| `start_session` | `path: str = "."` | Start a development session and generate a markdown sprint brief detailing goals, requirements, and previous handoffs. |
| `end_session` | `session_summary: str`, `known_issues: str = ""`, `path: str = "."` | Terminate sprint sessions, record milestones, and output handoff files without committing. |
| `prepare_commit` | `session_summary: str`, `path: str = "."` | Analyze modified/untracked files and generate suggested conventional git commit messages. |
| `commit_changes` | `message: str`, `path: str = "."` | Stage all files (`git add .`) and commit with the approved message. |

### C. Task & Todo Engine
Located in `brain/todo_engine.py`. These tools manage the project backlog.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `create_task` | `title: str`, `description: str`, `phase: str = ""`, `priority: str = "medium"`, `depends_on: str = ""`, `path: str = "."` | Create a new task tracking entry with priorities, phase limits, and dependency chains. |
| `update_task` | `task_id: str`, `title: str = ""`, `description: str = ""`, `phase: str = ""`, `status: str = ""`, `priority: str = ""`, `depends_on: str = ""`, `path: str = "."` | Update titles, descriptions, priorities, or statuses of a specific task. |
| `complete_task` | `task_id: str`, `notes: str = ""`, `path: str = "."` | Close a task, logging completing notes and moving it to completed records. |
| `next_task` | `path: str = "."` | Extract the highest priority task ready for development. |
| `blocked_tasks` | `path: str = "."` | List all tasks blocked by unmet dependency tasks. |
| `list_tasks` | `phase: str = ""`, `status: str = ""`, `path: str = "."` | Retrieve all registered tasks, optionally filtered by status or phase. |

### D. Phase & Milestone Management
Located in `brain/phase_manager.py`. These tools handle timeline bounds and releases.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_current_phase` | `path: str = "."` | Get the currently active development phase and status details. |
| `set_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Set the active phase (e.g. 'Phase 1 - Implementation'). Only tasks in this phase are in scope. |
| `complete_phase` | `notes: str = ""`, `path: str = "."` | Mark current phase as completed and register the transaction decision. |
| `next_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Conclude the current phase and advance directly to the next phase. |
| `list_phases` | `path: str = "."` | Display a list of all defined phases and their statuses. |
| `add_milestone` | `name: str`, `target_date: str = "", features: str = ""`, `path: str = "."` | Define a new project milestone tracking key features. |
| `list_milestones` | `path: str = "."` | Display all milestones and target completion dates. |

### E. PRD & Requirements Traceability
Located in `brain/prd_manager.py` and `brain/requirements.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_prd` | `document: str = "PRD"`, `path: str = "."` | Retrieve markdown PRD document contents (PRD, VISION, SCOPE, REQUIREMENTS). |
| `update_prd` | `document: str`, `content: str`, `path: str = "."` | Write or overwrite target specification markdown files. |
| `summarize_prd` | `path: str = "."` | Extract concise bulleted requirement summaries from all specifications. |
| `compare_work_to_prd` | `path: str = "."` | Audit task backlogs and contexts against the PRD to detect alignment gaps. |
| `extract_requirements` | `path: str = "."` | Extract structured requirement tags and keywords from the PRD markdown into `requirements.json`. |
| `verify_requirements` | `feature_name: str = ""`, `path: str = "."` | Scan codebase files to map requirement status based on keyword density. |
| `verify_outcome` | `task_id: str`, `path: str = "."` | Verify user entrypoints, validations, persistence schemas, and error pathways for a target task. |

### F. Workspace Sync & Reality Checks
Located in `brain/sync_engine.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `sync_workspace` | `path: str = "."` | Match Git branches, commits, and diff structures to the backlog to auto-detect finished work. |
| `verify_work` | `task_id: str`, `path: str = "."` | Compile verification confidence reports using tests, Git status, and guardian audits. |
| `project_dashboard` | `path: str = "."` | Generate a unified dashboard displaying workspace git states, tasks, phases, and overall health scores. |

### G. Sprint Handoffs
Located in `brain/handoff_engine.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_handoff` | `session_summary: str = ""`, `known_issues: str = ""`, `path: str = "."` | Save the current session log to `.project_brain/handoffs/` and mirror context briefs. |
| `get_last_handoff` | `path: str = "."` | Load the most recently saved handoff file to restore AI state. |
| `list_handoffs` | `path: str = "."` | Display a list of all historical handoff logs. |

### H. Architecture & Dependency Control
Located in `brain/guardian.py` and `brain/dependency.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `validate_architecture` | `path: str = "."` | Scan codebase imports against the forbidden and required technologies list. |
| `build_dependency_graph` | `path: str = "."` | Parse imports to build a complete connection graph across codebase modules. |
| `impact_analysis` | `file_path: str`, `path: str = "."` | Perform a BFS traversal of dependencies to map the blast radius (affected files) of a modified module. |

### I. Project Context CRUD
Located in `tools/context_mgmt.py`. Generic operations modifying `.project-context.json`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `init_context` | `path: str = "."` | Scans workspace config files to initialize a project context metadata file. |
| `get_context` | `dot_path: str = ""`, `path: str = "."` | Retrieve a field value from context JSON using dot path lookups (e.g. `project.name`). |
| `update_context` | `dot_path: str`, `value: str`, `path: str = "."` | Set or update a value in the context JSON. |
| `add_to_context_list` | `dot_path: str`, `item: str`, `path: str = "."` | Append strings or JSON objects to list fields in context. |
| `add_key_file` | `file_path: str`, `purpose: str`, `details: str = ""`, `root_path: str = "."` | Track critical codebase files and their architectural role. |
| `add_task` | `task_id: str`, `description: str`, `status: str = "pending"`, `branch: str = ""`, `notes: str = ""`, `path: str = "."` | Direct insert of active tasks into context records. |
| `add_decision` | `decision: str`, `reason: str`, `alternatives: str = ""`, `path: str = "."` | Log Architecture Decision Records (ADRs) to track project constraints. |
| `export_context_markdown` | `path: str = "."` | Export project context metadata to `.project-context.md` for external sharing. |
| `remove_context_item` | `dot_path: str`, `index: int`, `path: str = "."` | Remove list elements by index from context list fields. |
| `reset_context` | `path: str = "."` | Revert `.project-context.json` fields to defaults. |
| `project_info` | `path: str = "."` | Count files and directories, checking project runtime types. |

### J. Sandboxed File Operations
Located in `tools/file_ops.py`. Path traversals are validated using `security.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `read_file` | `path: str` | Read content from files in sandboxed directories. |
| `write_file` | `path: str`, `content: str` | Write text content, creating folders recursively. |
| `edit_file` | `path: str`, `old_string: str`, `new_string: str` | Replace exact target strings inside files (case/whitespace sensitive). |
| `delete_path` | `path: str` | Delete files or empty folders. |
| `delete_recursive` | `path: str` | Recursively delete file trees (danger operations). |
| `list_directory` | `path: str` | List directory contents and sizes. |
| `glob_files` | `pattern: str`, `base_path: str = "."` | Retrieve paths matching globs (e.g. `src/**/*.py`). |
| `create_directory` | `path: str` | Create missing directory paths. |

### K. Terminal, Git & Code Search Helpers
Located in `tools/terminal.py`, `tools/search.py`, and `tools/git_ops.py`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `run_command` | `command: str`, `timeout_seconds: int = 60`, `workdir: str = None` | Execute shell commands in authorized directories under strict timeout bounds. |
| `search_code` | `pattern: str`, `path: str = "."`, `glob_filter: str = None`, `max_results: int = 50` | Fast Ripgrep text search with Python fallbacks. |
| `git_status` | `repo_path: str = "."` | Print directory version status (`git status`). |
| `git_diff` | `repo_path: str = "."`, `staged: bool = False` | Return staged or unstaged modifications. |
| `git_log` | `repo_path: str = "."`, `max_count: int = 10` | Print recent commits. |
| `git_branch` | `repo_path: str = "."` | List local branches. |
| `git_add` | `repo_path: str = "."`, `files: str = "."` | Stage target modified files. |
| `git_commit` | `repo_path: str = "."`, `message: str = "update"` | Commit changes using Conventional Commits rules. |
| `git_create_branch` | `repo_path: str = "."`, `branch_name: str = ""` | Create and switch checkout branches. |

---

## 🧩 7. Prompts & Resources Reference

### Prompts
1. **`project-overview`** — Injects the entire project context JSON in markdown format, outputting development guidelines for the model.
2. **`code-review`** — Loads the project conventions and tech stack to provide specific checklists for reviewing code.
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
```

---

## 🔒 9. Security Sandbox

All file tools are sandboxed for security. Paths must resolve within directories in:
1. The server's current working directory.
2. `DEV_MCP_ALLOWED_DIRS` environment variable (colon-separated list of paths).
3. The user's home directory (`$HOME`).

*To restrict allowed directories:*
```bash
export DEV_MCP_ALLOWED_DIRS="/home/user/project1:/home/user/project2"
```

---

## 🔌 10. Troubleshooting & Connection Lifecycle

- **Stateful Connection:** Most AI clients (like Cursor or Claude Desktop) cache the active `stdio` pipe connection to the server process.
- **Out-of-Sync State:** If the server is updated or restarted, the client’s stdio connection can become stale, resulting in `EOF` or `client closing` errors.
- **Project Switching (No Context Leakage):** The global context cache in [app.py](file:///home/dev/Desktop/projects/mcp/dev-mcp/app.py) checks if the target root is different from the cached path during tool execution (`_root != target_root`), preventing tasks and metadata from leakages across projects.

### How to Reconnect Across Clients:
* **Cursor:** Go to **Settings** → **Features** → **MCP** → find `dev-mcp` and click **Restart**.
* **Claude Desktop:** Fully **Quit** the app from your taskbar/dock and reopen it to force Claude to spawn a new MCP process.
* **Cline / Roo Code:** Restart the extension or trigger a reconnect via `/mcp restart dev-mcp`.
* **Windsurf:** Reload the editor window or restart the workspace connection.
