# 🧠 dev-mcp: AI Engineering Operating System

`dev-mcp` is a custom **Model Context Protocol (MCP)** server that turns your AI assistants (Claude, Cursor, Gemini, Cline, Roo Code, Windsurf) into active **Technical Project Managers**. 

Rather than treating the AI as a stateless code generator, `dev-mcp` establishes a persistent **Project Brain** in your workspace directory. This allows you to switch between different AI models and platforms seamlessly without losing context, project goals, tasks, or guidelines.

## 🌟 Enhanced Startup Banner

The server now displays an eye‑catching banner on startup, showcasing the FastMCP version and deployment information with rich styling. This banner appears before the interactive hint line.

```bash
# Example banner output
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│                         ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█                        │
│                         █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀                        │
│                                                                              │
│                                                                              │
│                                                                              │
│                                FastMCP 3.4.2                                 │
│                            https://gofastmcp.com                             │
│                                                                              │
│                  🖥  Server:      dev-mcp, 3.4.2                              │
│                  🚀 Deploy free: https://horizon.prefect.io                  │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

The banner is rendered using the `rich` library and can be customized by editing the `_print_banner` function in `server.py`.

## 🕹️ Interactive Keyboard Shortcut Guide (`dev-mcp-guide`)

`dev-mcp` now includes an interactive terminal-based guide showing transport settings, MCP commands, and keyboard shortcut configurations:
```bash
dev-mcp-guide
```
Or, while running the `dev-mcp` server interactively in your terminal, press `?`, `h`, or `/` to temporarily open/overlay the guide directly from the active server process!

### Shortcuts:
- **← / →** or **Tab**: Switch tabs (General, Commands, Shortcuts).
- **↑ / ↓**: Scroll inside lists.
- **esc / q**: Close guide and return to the server loop.

> [!TIP]
> **Complete User Manual Available**
> For the comprehensive guide, including detailed setup, loops, slash commands, and a complete catalog of all 70 MCP tools with parameter signatures, see the **[docs/user_manual.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/user_manual.md)**.

---

## 👥 Author & Maintainer Profile

For issues, questions, or collaboration requests, contact:

* **Name:** Pranjal Yadav
* **Email:** [2k24.cs1l.2410719@gmail.com](mailto:2k24.cs1l.2410719@gmail.com)
* **Phone:** +91 9219920362
* **LinkedIn:** [linkedin.com/in/-pranjal22/](https://www.linkedin.com/in/-pranjal22/)
* **GitHub:** [github.com/pranjal2410719](https://github.com/pranjal2410719)

---

## 🚀 Full Setup & Installation Guide

### 1. Prerequisites
- **Python 3.10+**
- **Git**

### 2. Local Installation
Navigate to your `dev-mcp` directory and set up a virtual environment:

```bash
# Navigate to the server directory
cd /home/dev/Desktop/projects/mcp/dev-mcp

# Create a virtual environment using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# OR using standard python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## ⚙️ Configuring AI Clients (Cross-Platform)

Add the server command below to your editor of choice. 

* **Absolute Command Path:** `/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python`
* **Absolute Argument Path:** `/home/dev/Desktop/projects/mcp/dev-mcp/server.py`

### 1. Claude Desktop
Add the following to your configuration file:
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

### 2. Cursor
1. Go to **Settings** → **Features** → **MCP**.
2. Click **+ Add New MCP Server**.
3. Configure:
   - **Name:** `dev-mcp`
   - **Type:** `command`
   - **Command:** `/home/dev/Desktop/projects/mcp/dev-mcp/.venv/bin/python /home/dev/Desktop/projects/mcp/dev-mcp/server.py`
4. Click **Save**.

### 3. Windsurf
1. Open **Settings** → **Advanced** → **MCP Configurations**.
2. Add the configuration to your global list:
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

### 4. VS Code (Cline / Roo Code)
If using Cline, open the extension settings, select **MCP Settings**, and add:
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

## 👑 The Onboarding & Execution Workflow

`dev-mcp` establishes a strict project development lifecycle. The AI assistant evaluates codebase context dynamically, plans development sprints, tracks tasks, validates architecture requirements, syncs workspace files to real-world git events, and closes sessions safely.

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

### Step 1: Onboard a Codebase
Open any code repository on your computer and run:
1. `assess_project_readiness` — Evaluates directory files and computes a project readiness score (0-100%) and maturity level (Levels 0-5).
2. `doctor` — Run a complete diagnostic health check on your Project Brain, context, configuration, and setup.
3. **Bootstrap or Migrate:**
   - **For new/empty projects:** Run `bootstrap_project()` to write empty directories, project contexts, and milestones.
   - **For existing legacy codebases:** Run `adopt_existing_project()` to scan language extensions, parse the current `README.md` to draft goals, and populate initial task backlogs.

### Step 2: Set the Scope
Open the generated `.project_brain/prd/PRD.md` file and verify your goals. Run:
1. `extract_requirements` — Extracts requirements and keywords into `requirements.json`.
2. `start_session` — Bootstraps a development sprint and prints a Markdown brief for the model.

### Step 3: Run the Session Loop
During active coding, keep alignment checked:
1. `project_dashboard` — View uncommitted git changes, milestones, active tasks, and code health logs.
2. `next_best_action` — Asks the engine to determine the next unblocked priority task.
3. `sync_workspace` — Matches physical file changes and commit history to detect completed work.
4. `verify_work` — Gathers file existences, test paths, and guardian violations to compile a verification dossier.
5. `verify_outcome` — Audits the code structure for database mutations, inputs, and routing to verify business goals.

### Step 4: Safe Session Conclusion
When the task is complete, close the session without corrupting git history:
1. `end_session` — Generates a markdown session handoff log.
2. `prepare_commit` — Analyzes changes and suggests a conventional commit message (e.g. `feat(auth): add login form`).
3. `commit_changes` — Stages and commits changes with the approved message.

### Step 5: Project Lifecycle & Resetting
If you need to archive, rotate, or re-initialize a project context:
1. `archive_project_brain` — Moves your active context and project brain configurations to `.project_brain_archive/` with a timestamp to preserve history.
2. `reset_project_brain` — Wipes the context store and `.project_brain` files for the target folder, leaving your source code and git repository untouched.

---

## 🛠️ Complete MCP Tool Reference (70 Tools)

Here is the exhaustive catalog of all 70 registered tools on the `dev-mcp` server, grouped logically by module and function.

### 1. Onboarding & Diagnostics (`brain/project_readiness.py`)
These tools handle project onboarding, configuration sanity auditing, resets, and archiving.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `assess_project_readiness` | `path: str = "."` | Scan the workspace and evaluate its onboarding readiness score (0-100%) against required Project Brain documents. |
| `project_readiness_report` | `path: str = "."` | Generate a formatted Markdown project readiness report showing missing files, scoring audit, and recommended actions. |
| `bootstrap_project` | `path: str = "."` | Auto-generate template files and directories (PRD, milestones, active tasks, config yaml) to instantly onboard an unknown repository. |
| `adopt_existing_project` | `path: str = "."` | Scan an existing legacy codebase (directories, package lists, readmes) and generate context, PRDs, milestones, and audit tasks. |
| `doctor` | `path: str = "."` | Check the diagnostic health and configuration integrity of the Project Brain and MCP server. |
| `reset_project_brain` | `path: str = "."` | Wipe all Project Brain configuration, tasks, and context metadata inside the selected project. Leaves git and source code untouched. |
| `archive_project_brain` | `path: str = "."` | Archive current Project Brain settings and context files to `.project_brain_archive/` before a reset or pivot, preserving history. |

### 2. Session Orchestration (`brain/orchestrator.py`)
These tools drive the session sprint loop, planning, and safe Git committing.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_project_brain` | `path: str = "."` | Generate a complete aggregated Project Brain dashboard showing current status, phase, active/blocked tasks, recent changes, and recommendations. |
| `next_best_action` | `path: str = "."` | Intelligently calculate and recommend the next best task to work on based on phase, priority, dependencies, and file hints. |
| `start_session` | `path: str = "."` | Start a development session. Loads state, PRD, active tasks, and latest handoff to generate a detailed Session Brief for the AI. |
| `end_session` | `session_summary: str`, `known_issues: str = ""`, `path: str = "."` | End the current session, update progress, and generate a handoff file (does not auto-commit changes). |
| `prepare_commit` | `session_summary: str`, `path: str = "."` | Analyze modified workspace files and generate a suggested conventional git commit message and summary for approval. |
| `commit_changes` | `message: str`, `path: str = "."` | Stage all workspace changes and commit them to Git with the approved commit message. |

### 3. Task & Todo Management (`brain/todo_engine.py`)
These tools support granular planning, priorities, and dependency-aware task backlogs.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `create_task` | `title: str`, `description: str`, `phase: str = ""`, `priority: str = "medium"`, `depends_on: str = ""`, `path: str = "."` | Create a new task with phase, priority, dependencies, and description. |
| `update_task` | `task_id: str`, `title: str = ""`, `description: str = ""`, `phase: str = ""`, `status: str = ""`, `priority: str = ""`, `depends_on: str = ""`, `path: str = "."` | Update a task's status, priority, or description by ID. |
| `complete_task` | `task_id: str`, `notes: str = ""`, `path: str = "."` | Mark a task as completed with optional notes. |
| `next_task` | `path: str = "."` | Get the highest-priority task that is ready to work on (dependencies met, current phase). |
| `blocked_tasks` | `path: str = "."` | List all tasks that are blocked, either by dependencies or explicitly. |
| `list_tasks` | `phase: str = ""`, `status: str = ""`, `path: str = "."` | List all active tasks, optionally filtered by phase or status. |

### 4. Phase & Milestone Management (`brain/phase_manager.py`)
These tools handle project timeline scoping, phase progression, and release milestones.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_current_phase` | `path: str = "."` | Get the current active phase and its status. |
| `set_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Set the current active development phase. Only tasks in this phase are considered 'in scope'. |
| `complete_phase` | `notes: str = ""`, `path: str = "."` | Mark the current phase as completed and optionally advance to the next phase. |
| `next_phase` | `phase_name: str`, `description: str = ""`, `path: str = "."` | Mark current phase as complete and advance to the next phase in sequence. |
| `list_phases` | `path: str = "."` | List all phases and their status (completed, active, pending). |
| `add_milestone` | `name: str`, `target_date: str = ""`, `features: str = ""`, `path: str = "."` | Define a milestone with a target date and associated features. |
| `list_milestones` | `path: str = "."` | Show all milestones and their status. |

### 5. PRD & Requirements Traceability (`brain/prd_manager.py` & `brain/requirements.py`)
These tools manage scope files and check if the implemented codebase corresponds to the PRD.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_prd` | `document: str = "PRD"`, `path: str = "."` | Retrieve a PRD document (PRD, VISION, SCOPE, REQUIREMENTS). Returns the content of the specified document. |
| `update_prd` | `document: str`, `content: str`, `path: str = "."` | Create or update a PRD document (PRD, VISION, SCOPE, REQUIREMENTS). |
| `summarize_prd` | `path: str = "."` | Summarize key requirements from PRD documents into a concise bullet list. |
| `compare_work_to_prd` | `path: str = "."` | Compare current project context and tasks against PRD requirements to check alignment. |
| `extract_requirements` | `path: str = "."` | Parse PRD markdown files to extract structured requirements and save them into `requirements.json`. |
| `verify_requirements` | `feature_name: str = ""`, `path: str = "."` | Scan codebase to map requirement keywords and verify their implementation status and feature coverage. |
| `verify_outcome` | `task_id: str`, `path: str = "."` | Perform outcome audits verifying user flows, business goals, and objective completion based on target tasks. |

### 6. Workspace Sync & Verification (`brain/sync_engine.py`)
These tools check if code changes match physical files and track completeness metrics.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `sync_workspace` | `path: str = "."` | Scan the physical workspace (Git diff, new files, current branch, commits) and compare to the Todo plan to auto-detect finished work. |
| `verify_work` | `task_id: str`, `path: str = "."` | Perform deep sanity, test, git diff, and architecture checks against a task to output a reality verification dossier. |
| `project_dashboard` | `path: str = "."` | Generate a unified Project Manager Dashboard combining phase state, todo progress, git status, architecture violations, and a project health score. |

### 7. Handoff & Sprint History (`brain/handoff_engine.py`)
These tools record and retrieve AI context handoffs across sessions.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `generate_handoff` | `session_summary: str = ""`, `known_issues: str = ""`, `path: str = "."` | Generate a session summary capturing what was done, what's next, and current project state for handoff to another AI. |
| `get_last_handoff` | `path: str = "."` | Retrieve the most recent AI handoff document so a new AI session has full context. |
| `list_handoffs` | `path: str = "."` | List all AI session handoffs with dates. |

### 8. Architecture & Dependency Control (`brain/guardian.py` & `brain/dependency.py`)
These tools ensure structural health, dependency blast radius checks, and technology rules enforcement.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `validate_architecture` | `path: str = "."` | Scan the codebase and validate imports/technologies against the project's architectural guidelines and forbidden tools. |
| `build_dependency_graph` | `path: str = "."` | Scan files and construct a complete mapping of dependencies and references in the project. |
| `impact_analysis` | `file_path: str`, `path: str = "."` | Calculate direct and transitive downstream files affected if a given file is modified. |

### 9. Context Management (`tools/context_mgmt.py`)
These tools provide generic getters/setters for `.project-context.json`.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `init_context` | `path: str = "."` | Initialize or auto-detect project context. Scans project files to detect tech stack, languages, and frameworks. |
| `get_context` | `dot_path: str = ""`, `path: str = "."` | Get the full project context as formatted JSON/text. Optionally filter by dot path (e.g. `tech_stack.languages`). |
| `update_context` | `dot_path: str`, `value: str`, `path: str = "."` | Update a specific field in the project context using dot notation (e.g. `project.description`). |
| `add_to_context_list` | `dot_path: str`, `item: str`, `path: str = "."` | Add an item to a list field in the context (e.g. `tech_stack.languages`, `key_files`). Supports strings or JSON strings. |
| `add_key_file` | `file_path: str`, `purpose: str`, `details: str = ""`, `root_path: str = "."` | Register a key file with its purpose and optional details in the project context. |
| `add_task` | `task_id: str`, `description: str`, `status: str = "pending"`, `branch: str = ""`, `notes: str = ""`, `path: str = "."` | Add an active task to the project context. |
| `add_decision` | `decision: str`, `reason: str`, `alternatives: str = ""`, `path: str = "."` | Log an architecture decision record (ADR) in the project context. |
| `export_context_markdown` | `path: str = "."` | Export the project context as a Markdown document for sharing with other LLMs and AI tools. |
| `remove_context_item` | `dot_path: str`, `index: int`, `path: str = "."` | Remove an item from a list in the project context by index. |
| `reset_context` | `path: str = "."` | Reset the project context to default values (clears all data). |
| `project_info` | `path: str = "."` | Get information about the current project environment (languages, frameworks, file counts). |

### 10. File Operations (`tools/file_ops.py`)
These tools provide sandbox-constrained file manipulation utilities.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `read_file` | `path: str` | Read the contents of a file at the given path. |
| `write_file` | `path: str`, `content: str` | Write content to a file, creating it if it doesn't exist. |
| `edit_file` | `path: str`, `old_string: str`, `new_string: str` | Edit a file by replacing an exact string with a new string. Use this for targeted code changes. |
| `delete_path` | `path: str` | Delete a file or an empty directory. |
| `delete_recursive` | `path: str` | Recursively delete a file or directory tree. Use with caution. |
| `list_directory` | `path: str` | List files and directories inside a given directory. |
| `glob_files` | `pattern: str`, `base_path: str = "."` | Find files matching a glob pattern (e.g. `**/*.ts`, `src/**/*.py`). |
| `create_directory` | `path: str` | Create one or more directories (like `mkdir -p`). |

### 11. Terminal, Git & Code Search (`tools/terminal.py`, `tools/search.py` & `tools/git_ops.py`)
These tools provide controlled shell command runs, pattern search, and Git operations.

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `run_command` | `command: str`, `timeout_seconds: int = 60`, `workdir: str = None` | Run a shell command and return its output. Always set a reasonable timeout. Avoid destructive commands. |
| `search_code` | `pattern: str`, `path: str = "."`, `glob_filter: str = None`, `max_results: int = 50` | Search for a text pattern across files in the project using ripgrep (or Python fallback). |
| `git_status` | `repo_path: str = "."` | Show the working tree status (git status). |
| `git_diff` | `repo_path: str = "."`, `staged: bool = False` | Show staged and unstaged changes (git diff). |
| `git_log` | `repo_path: str = "."`, `max_count: int = 10` | Show recent commit history (git log). |
| `git_branch` | `repo_path: str = "."` | List local branches (git branch). |
| `git_add` | `repo_path: str = "."`, `files: str = "."` | Stage file(s) for commit (git add). |
| `git_commit` | `repo_path: str = "."`, `message: str = "update"` | Commit staged changes with a message (git commit). |
| `git_create_branch` | `repo_path: str = "."`, `branch_name: str = ""` | Create and switch to a new git branch (git checkout -b). |

---

## 🧩 Prompts Reference

The server registers **4 Prompt Templates** that can be loaded in supported MCP Clients:

1. **`project-overview`** — Injects the entire project context JSON in markdown format, outputting development guidelines for the model.
2. **`code-review`** — Loads the project conventions and tech stack to provide specific checklists for reviewing code.
3. **`architectural-decision`** — Provides a structured markdown template to record Architecture Decision Records (ADRs).
4. **`feature-plan`** — Generates a blueprint template for planning branches, milestones, tasks, and target files.

---

## 📦 Resources Reference

The server exposes **2 resources** matching the current active project root:

1. **`project://context/json`** — Returns `.project-context.json` content as JSON.
2. **`project://context/markdown`** — Returns `.project-context.json` context parsed as a Markdown layout.

---

## ⚙️ Workspace Configuration (`.project_brain/config.yaml`)

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

## 🔒 Security Sandbox

All file tools are sandboxed for security. Paths must resolve within directories in:
1. The server's current working directory.
2. `DEV_MCP_ALLOWED_DIRS` environment variable (colon-separated list of paths).
3. The user's home directory (`$HOME`).

*To restrict allowed directories:*
```bash
export DEV_MCP_ALLOWED_DIRS="/home/user/project1:/home/user/project2"
```

---

## 🔌 Troubleshooting & Connection Lifecycle

When developing or updating code in `dev-mcp`, keep in mind how MCP clients handle the process lifecycle:
- **Stateful Connection:** Most AI clients (like Cursor or Claude Desktop) cache the active `stdio` pipe connection to the server process.
- **Out-of-Sync State:** If the server is updated or restarted, the client’s stdio connection can become stale, resulting in `EOF` or `client closing` errors.
- **Project Switching (No Context Leakage):** The global context cache in [app.py](file:///home/dev/Desktop/projects/mcp/dev-mcp/app.py) checks if the target root is different from the cached path during tool execution (`_root != target_root`), preventing tasks and metadata from leakages across projects.

### How to Reconnect Across Clients:
* **Cursor:** Go to **Settings** → **Features** → **MCP** → find `dev-mcp` and click **Restart**.
* **Claude Desktop:** Fully **Quit** the app from your taskbar/dock and reopen it to force Claude to spawn a new MCP process.
* **Cline / Roo Code:** Restart the extension or trigger a reconnect via `/mcp restart dev-mcp`.
* **Windsurf:** Reload the editor window or restart the workspace connection.

---

## 🧪 Running Validation Tests

Ensure server correctness and E2E workflow consistency by executing the pipeline script:

```bash
.venv/bin/python tests/validate_mcp_flow.py
```

For guidelines on coding conventions, code style, and how to write custom tools for this server, see **[CONTRIBUTING.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/CONTRIBUTING.md)**.
