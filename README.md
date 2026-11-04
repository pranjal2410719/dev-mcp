# 🧠 dev-mcp: AI Engineering Operating System (v2.1.0)

`dev-mcp` is a production-grade **Model Context Protocol (MCP)** server that turns your AI assistants (Claude, Cursor, Gemini, Cline, Roo Code, Windsurf, Antigravity CLI) into autonomous **Technical Project Managers and Desktop Automation Engineers**. 

Rather than treating LLMs as stateless code generators, `dev-mcp` establishes a persistent **Project Brain** directly in your workspace repository. It preserves context, PRD specifications, phase timelines, task dependencies, architectural guards, and desktop verification states across multiple AI sessions and platforms.

---

## 👥 Author & Maintainer Profile

For inquiries, support, or technical contributions, reach out to:

* **Name:** Pranjal Yadav
* **Email:** [2k24.cs1l.2410719@gmail.com](mailto:2k24.cs1l.2410719@gmail.com)
* **Phone:** +91 9219920362
* **LinkedIn:** [linkedin.com/in/-pranjal22/](https://www.linkedin.com/in/-pranjal22/)
* **GitHub:** [github.com/pranjal2410719](https://github.com/pranjal2410719)

---

## ⚡ What's New in v2.1.0?

* **84 Registered MCP Tools across 18 specialized modules.**
* **Dynamic Tool Profiling (`DEV_MCP_PROFILE`)**: Slash LLM prompt token consumption by up to **75%** by loading only the tools relevant to your workflow (`code`, `planning`, `audit`, `desktop`, or `all`).
* **Desktop GUI Automation & Verification (`tools/desktop_ops.py`)**: Direct integration with `agent-desktop` (Linux AT-SPI / X11 / Wayland, macOS, Windows) for GUI inspection, clicking, typing, and desktop window snapshots.
* **High-Speed Filesystem & Search**:
  - **26.2× faster** path validation in `security.py` (0.087ms vs 2.28ms).
  - Sliced reads (`start_line`, `end_line`), line numbering, and safety truncation (>2,500 lines).
  - Atomic writing via temporary files and `os.replace`.
  - In-place string editing with exact `count` control and whitespace mismatch assistance.
  - Multi-file atomic batch replacements (`batch_replace`).
  - File metadata inspection (`file_info`).
  - Automatic noise filtering (`.git`, `node_modules`, `__pycache__`, `.venv`, `.next`, `dist`, `build`).
  - Native Ripgrep (`rg`) search with Python regex fallback.
* **AST Dependency & Blast Radius Caching**: `mtime`-backed AST parse caching (`_FILE_PARSE_CACHE`) reduces dependency traversal times to sub-millisecond speeds.
* **Persistent Git Hook Automation (`install_git_hooks`)**: Automatically generates a Git pre-commit hook that syncs `.project_brain` on every native terminal commit.

---

## 🏗️ Architecture Overview

```text
                  Developer / AI Host Client
      (Cursor, Claude Desktop, Windsurf, Antigravity CLI)
                              │
                              ▼
                       dev-mcp Server
               (FastMCP 3.4.2 · Python 3.10+)
                              │
  ┌───────────────────────────┼───────────────────────────┐
  │                           │                           │
  ▼                           ▼                           ▼
Project Workspace       Security Sandbox           Desktop Automation
├── Source Files        ├── Path Jailing (safe)     ├── agent-desktop CLI
├── Git Repository      ├── Allowed Dirs (lab)      ├── AT-SPI Accessibility
└── .project_brain/     └── Command Filter          └── Screen / Window Ops
    ├── config.yaml
    ├── prd/
    ├── tasks/
    └── handoffs/
```

---

## 🌟 Enhanced Startup Banner

On server boot, `dev-mcp` renders a rich visual banner with active profile status and host diagnostics:

```bash
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│                         ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█                        │
│                         █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀                        │
│                                                                              │
│                                FastMCP 3.4.2                                 │
│                            https://gofastmcp.com                             │
│                                                                              │
│                  🖥  Server:      dev-mcp, 3.4.2                              │
│                  🎯 Profile:     ALL (84 Tools / 18 Modules)                 │
│                  🚀 Deploy free: https://horizon.prefect.io                  │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 🎯 Tool Profiles & Token Optimization (`DEV_MCP_PROFILE`)

Loading 84 tools into an LLM context consumes ~12,000 system prompt tokens on every turn. Set the `DEV_MCP_PROFILE` environment variable in your client configuration to load only what you need:

| Profile | Token Overhead | Reduction | Modules Loaded | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `code` | ~4,200 tokens | **66.4%** | File Ops, Search, Context, Git Ops, Terminal | Fast daily coding and refactoring sprints |
| `planning` | ~3,800 tokens | **69.6%** | PRD Manager, Todo Engine, Phase Manager, Context | Technical project management and roadmaps |
| `audit` | ~4,500 tokens | **64.0%** | Readiness, Guardian, Dependency, Doctor, Outcome | Architecture review and security audits |
| `desktop` | ~3,100 tokens | **75.2%** | Desktop Ops, Terminal, File Ops | GUI testing and desktop automation |
| `all` (default) | ~12,500 tokens | 0% | All 18 modules (84 tools) | Full autonomous development workflows |

To check the active profile programmatically, call `get_dev_mcp_profile()`.

---

## 🕹️ Interactive Keyboard Shortcut Guide (`dev-mcp-guide`)

Launch the built-in interactive terminal helper at any time:
```bash
dev-mcp-guide
```
Or, while running the `dev-mcp` server interactively in a terminal, press `?`, `h`, or `/` to display the modal overlay.

* **← / →** or **Tab**: Switch tabs (General, Commands, Shortcuts).
* **↑ / ↓**: Scroll list entries.
* **esc / q**: Return to the server loop.

---

## 🚀 Full Setup & Installation

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- *(Optional)* **agent-desktop** (`npm install -g agent-desktop`) for GUI testing on Linux, macOS, or Windows.
- *(Optional)* **ripgrep** (`sudo apt install ripgrep`) for high-speed file searches.

### 2. Local Installation
```bash
# Clone or navigate to the repository
cd /path/to/dev-mcp

# Setup virtual environment with uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .

# Or using standard python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## ⚙️ Configuring AI Clients

### 1. Claude Desktop
Add to `~/.config/Claude/claude_desktop_config.json` (Linux/macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):
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

### 2. Cursor
1. Go to **Settings** → **Features** → **MCP**.
2. Click **+ Add New MCP Server**.
3. Set Name to `dev-mcp`, Type to `command`, and Command to:
   ```bash
   /path/to/dev-mcp/.venv/bin/python /path/to/dev-mcp/server.py
   ```

### 3. Windsurf
Add to your `mcp_config.json`:
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

### 4. Antigravity CLI (Google DeepMind)
Add to `~/.gemini/antigravity-cli/mcp_config.json`:
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

## 👑 The Onboarding & Execution Workflow

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

## 🛠️ Complete MCP Tool Catalog (84 Tools)

### 1. Core Onboarding & Diagnostics (`brain/project_readiness.py`)
- `assess_project_readiness(path=".")`: Scan directory and calculate readiness score (0-100%).
- `project_readiness_report(path=".")`: Generate formatted Markdown readiness report.
- `bootstrap_project(path=".")`: Initialize PRD templates, milestones, and brain structure.
- `adopt_existing_project(path=".")`: Scan existing legacy repository and draft PRD, context, and backlog.
- `doctor(path=".")`: Run diagnostic health audit across 7 layers.
- `reset_project_brain(path=".")`: Reset project metadata while preserving source code and git.
- `archive_project_brain(path=".")`: Backup project brain state into `.project_brain_archive/`.
- `create_project_workspace(name, template="blank", path=".")`: Create isolated sibling workspace directory.

### 2. Session Orchestration (`brain/orchestrator.py`)
- `generate_project_brain(path=".")`: Consolidate current sprint metrics into a single dashboard.
- `next_best_action(path=".")`: Recommend the highest-priority unblocked task.
- `start_session(path=".")`: Begin a sprint and generate an AI task briefing.
- `end_session(session_summary, known_issues="", path=".")`: Conclude sprint and record handoff.
- `prepare_commit(session_summary, path=".")`: Suggest conventional commit message based on Git diff.
- `commit_changes(message, path=".")`: Stage workspace changes and commit cleanly.

### 3. Task & Todo Engine (`brain/todo_engine.py`)
- `create_task(title, description, phase="", priority="medium", depends_on="", path=".")`: Add task.
- `update_task(task_id, status="", priority="", title="", path=".")`: Update task attributes.
- `complete_task(task_id, notes="", path=".")`: Close task with completion notes.
- `next_task(path=".")`: Get next ready task.
- `blocked_tasks(path=".")`: List tasks blocked by unfulfilled dependencies.
- `list_tasks(phase="", status="", priority="", path=".")`: Query tasks by phase, status, or priority.

### 4. Phase & Milestone Management (`brain/phase_manager.py`)
- `get_current_phase(path=".")`: Retrieve active development phase.
- `set_phase(phase_name, description="", path=".")`: Set active scope phase.
- `complete_phase(notes="", path=".")`: Conclude current phase.
- `next_phase(phase_name, description="", path=".")`: Advance to next phase.
- `list_phases(path=".")`: List all defined phases.
- `add_milestone(name, target_date="", features="", path=".")`: Define project milestone.
- `list_milestones(path=".")`: Enumerate all milestones.

### 5. PRD & Requirements Traceability (`brain/prd_manager.py`, `brain/requirements.py`)
- `get_prd(document="PRD", path=".")`: Read markdown PRD specification document.
- `update_prd(document, content, path=".")`: Update PRD specification document.
- `summarize_prd(path=".")`: Generate bullet-point requirements summary.
- `compare_work_to_prd(path=".")`: Audit backlog against PRD specifications.
- `extract_requirements(path=".")`: Extract structured requirements into `requirements.json`.
- `verify_requirements(feature_name="", path=".")`: Verify code implementation coverage against PRD.
- `verify_outcome(task_id, path=".")`: Deep outcome audit verifying end-to-end user journeys.

### 6. Workspace Sync & Verification (`brain/sync_engine.py`)
- `sync_workspace(path=".")`: Match Git commits and physical changes to tasks to auto-close work.
- `verify_work(task_id, path=".")`: Gather git diff, tests, and architecture rules to compile verification dossier.
- `project_dashboard(path=".")`: Unified manager dashboard combining Git, tasks, and code health.

### 7. Sprint Handoffs (`brain/handoff_engine.py`)
- `generate_handoff(session_summary="", known_issues="", path=".")`: Save sprint handoff log.
- `get_last_handoff(path=".")`: Load latest session handoff.
- `list_handoffs(path=".")`: List historical handoffs with timestamps.

### 8. Architecture & Dependency Control (`brain/guardian.py`, `brain/dependency.py`)
- `validate_architecture(path=".")`: Check code imports against forbidden and required technology rules.
- `build_dependency_graph(path=".")`: Build complete dependency graph with cached AST parser.
- `impact_analysis(file_path, path=".")`: Calculate blast radius and affected downstream files before refactoring.

### 9. Context Management (`tools/context_mgmt.py`)
- `init_context(path=".")`: Initialize or auto-detect project context.
- `get_context(dot_path="", path=".")`: Query context field using dot notation.
- `update_context(dot_path, value, path=".")`: Set context field value.
- `add_to_context_list(dot_path, item, path=".")`: Append item to list field.
- `add_key_file(file_path, purpose, details="", root_path=".")`: Track critical codebase file.
- `add_task(task_id, description, status="pending", branch="", notes="", path=".")`: Add task record.
- `add_decision(decision, reason, alternatives="", path=".")`: Log Architecture Decision Record (ADR).
- `export_context_markdown(path=".")`: Export project context to `.project-context.md`.
- `remove_context_item(dot_path, index, path=".")`: Remove item from list by index.
- `reset_context(path=".")`: Reset context to defaults.
- `project_info(path=".")`: Inspect project file count, frameworks, and runtime metrics.

### 10. High-Performance File Operations (`tools/file_ops.py`)
- `read_file(path, start_line=None, end_line=None, line_numbers=False)`: Read sandboxed files with slicing and safety limits.
- `write_file(path, content, append=False)`: Atomic file writes with directory auto-creation and append support.
- `edit_file(path, old_string, new_string, count=None)`: Surgical in-place editing with whitespace mismatch detection.
- `batch_replace(file_paths, old_string, new_string)`: Atomic multi-file text replacement.
- `file_info(path)`: Get file size, line count, permissions, and modification timestamp.
- `delete_path(path)`: Delete single file or empty folder.
- `delete_recursive(path)`: Recursively delete folder trees (blocked in `safe` mode).
- `list_directory(path)`: List directory entries with human-readable sizes and noise filtering.
- `glob_files(pattern, base_path=".")`: Find files with glob patterns and noise filtering.
- `create_directory(path)`: Recursively create directory paths (`mkdir -p`).

### 11. Code Search & Terminal Execution (`tools/search.py`, `tools/terminal.py`)
- `search_code(pattern, path=".", glob_filter=None, max_results=50, context_lines=0)`: High-speed search using Ripgrep (`rg`) with regex fallback.
- `run_command(command, timeout_seconds=60, workdir=None)`: Execute shell command inside sandbox with safety filtering.

### 12. Git Operations & Automation (`tools/git_ops.py`)
- `git_status(repo_path=".")`: Get working tree status.
- `git_diff(repo_path=".", staged=False)`: View staged or unstaged diffs.
- `git_log(repo_path=".", max_count=10)`: Inspect commit history.
- `git_branch(repo_path=".")`: List local branches.
- `git_add(repo_path=".", files=".")`: Stage files for commit.
- `git_commit(repo_path=".", message="update")`: Commit staged files.
- `git_create_branch(repo_path=".", branch_name="")`: Create and checkout branch.
- `install_git_hooks(repo_path=".")`: Install Git pre-commit hook to automatically sync `.project_brain`.

### 13. Desktop GUI Automation & Verification (`tools/desktop_ops.py`)
- `desktop_status()`: Inspect `agent-desktop` CLI installation and AT-SPI accessibility bus.
- `desktop_list_apps()`: List active desktop processes and window titles.
- `desktop_list_windows()`: List desktop window IDs and geometry bounds.
- `desktop_snapshot(app="")`: Capture accessibility tree structure of running applications.
- `desktop_find(name="", role="", app="")`: Locate UI elements (buttons, inputs, menus) by text or role.
- `desktop_click(name="", role="", app="")`: Trigger native mouse click on target element.
- `desktop_type(text, app="")`: Send native keyboard keystrokes to active window.
- `desktop_verify_element(name, role="", app="")`: Verify that expected GUI component exists and is visible.
- `desktop_screenshot(output_path="screenshot.png")`: Capture full desktop display screenshot.

### 14. Server Profiling (`server.py`)
- `get_dev_mcp_profile()`: Inspect active profile mode, loaded modules, and tool counts.

---

## 🔒 Security Sandbox & Safety Modes

All file and process operations are governed by `security.py`:
- **`safe` (Default)**: Workspace Lock active. Commands jailed to active project root. Recursive deletions and destructive commands (`sudo`, `mkfs`, `rm -rf`, `git reset --hard`) are blocked.
- **`trusted`**: Workspace Lock active. Folder deletions and checkout operations permitted within project bounds.
- **`lab`**: Workspace Lock disabled. Allows operations across allowed directories list (`DEV_MCP_ALLOWED_DIRS`).

For security specifications, see **[docs/security.md](docs/security.md)**.

---

## 📚 In-Depth Documentation

- **[User Manual & Developer Guide](docs/user_manual.md)**: Complete guide to all 84 tools with parameter signatures and examples.
- **[v2.1.0 Release Notes](docs/release-notes-v2.1.0.md)**: Performance benchmarks and upgrade guides.
- **[Architecture Specification](docs/architecture-v2.md)**: Architecture, data structures, and multi-agent isolation.
- **[Security Model](docs/security.md)**: Workspace Lock, safety modes, and command authorization.
- **[Multi-Workspace Guide](docs/workspaces.md)**: Managing sibling workspaces and subagent isolation.
- **[Antigravity CLI Integration](docs/antigravity.md)**: DeepMind Antigravity CLI workflows.
- **[Open Design Integration](docs/open-design.md)**: Design-to-code metadata synchronization.

---

## 🧪 Testing & Validation

```bash
# Run unit and optimization test suites
.venv/bin/python -m unittest discover -s tests -p "*.py" -v

# Run the end-to-end MCP workflow verification
.venv/bin/python tests/validate_mcp_flow.py

# Verify optimization benchmarks
.venv/bin/python tests/test_optimizations.py
```
