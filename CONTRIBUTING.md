# 🤝 Contributing to dev-mcp

First off, thank you for showing interest in contributing to **`dev-mcp` (AI Engineering Operating System)**! 

This document outlines the architecture, code standards, setup guides, and contribution guidelines to help you get started quickly.

---

## 👥 Lead Maintainer Contact Info

For questions, community syncs, or active partnerships, feel free to reach out to the project founder:

* **Name:** Pranjal Yadav
* **Email:** [2k24.cs1l.2410719@gmail.com](mailto:2k24.cs1l.2410719@gmail.com)
* **Phone:** +91 9219920362
* **LinkedIn:** [linkedin.com/in/-pranjal22/](https://www.linkedin.com/in/-pranjal22/)
* **GitHub Profile:** [github.com/pranjal2410719](https://github.com/pranjal2410719)
* **Project Repository:** [github.com/pranjal2410719/dev-mcp](https://github.com/pranjal2410719/dev-mcp)

---

## 📐 Architecture Overview & Module Layout

The codebase of `dev-mcp` is cleanly separated into three layers: **Core**, **Tools**, and **Brain**, comprising **15 tool modules** and **71 registered MCP tools** (along with 2 resources and 4 prompts).

```mermaid
graph TD
    server[server.py Entry Point] --> app[app.py FastMCP Instance]
    server --> tools[tools/ Generic Tools]
    server --> brain[brain/ Specialized PM Engines]
    server --> prompts[prompts/ Definitions]
    server --> resources[resources/ Definitions]
    
    app --> context[context.py ProjectContext]
    app --> security[security.py validate_path]
    
    tools --> file_ops[file_ops.py]
    tools --> search[search.py]
    tools --> git_ops[git_ops.py]
    tools --> terminal[terminal.py]
    tools --> context_mgmt[context_mgmt.py]
    
    brain --> prd[prd_manager.py]
    brain --> phase[phase_manager.py]
    brain --> todo[todo_engine.py]
    brain --> handoff[handoff_engine.py]
    brain --> orchestrator[orchestrator.py]
    brain --> guardian[guardian.py]
    brain --> dep[dependency.py]
    brain --> sync[sync_engine.py]
    brain --> reqs[requirements.py]
    brain --> readiness[project_readiness.py]
```

### 1. Core Layer
* **[server.py](server.py)**: The main execution script. Implements a dual-mode entrypoint: runs stdio JSON-RPC directly for MCP host clients in non-interactive pipe mode, or runs a background daemon server thread with an interactive `/dev/tty` shortcut listener and Rich ASCII banner in TTY mode.
* **[app.py](app.py)**: Manages shared server state, initializes the `FastMCP` instance, and hosts the context loader (`load_context`). The loader prevents cross-project state leakage by detecting when the requested directory differs from the cached instance.
* **[context.py](context.py)**: Implements the `ProjectContext` class, which manages key-value store transactions against `.project-context.json` using dot-notation, handles defaults, and generates markdown reports for LLM clients.
* **[security.py](security.py)**: The security controller. Enforces Workspace Lock (strict jailing of file operations and paths to the active project root in `safe` and `trusted` modes), provides stack-inspected onboarding bypass for `bootstrap_project`, `create_project_workspace`, and `adopt_existing_project`, and implements 3 configurable safety modes (`safe`, `trusted`, `lab`).

### 2. Tools Layer (Generic — 28 Tools across 5 Modules)
Stateless utility wrappers exposing standard operating system functions to the LLM:
* **[tools/file_ops.py](tools/file_ops.py)**: Handles sandboxed file manipulation (8 tools: `read_file`, `write_file`, `edit_file`, `delete_path`, `delete_recursive`, `list_directory`, `glob_files`, `create_directory`).
* **[tools/search.py](tools/search.py)**: Ripgrep-based code pattern search with a robust, pure-Python fallback search if `rg` is not installed on the system (1 tool: `search_code`).
* **[tools/terminal.py](tools/terminal.py)**: Safely runs local terminal commands with strict timeouts and pattern blocklists (1 tool: `run_command`).
* **[tools/git_ops.py](tools/git_ops.py)**: Operates local Git repositories (7 tools: `git_status`, `git_diff`, `git_log`, `git_branch`, `git_add`, `git_commit`, `git_create_branch`).
* **[tools/context_mgmt.py](tools/context_mgmt.py)**: Direct getters and setters to query, modify, add, and remove records in `.project-context.json` (11 tools: `init_context`, `get_context`, `update_context`, `add_to_context_list`, `add_key_file`, `add_task`, `add_decision`, `export_context_markdown`, `remove_context_item`, `reset_context`, `project_info`).

### 3. Brain Layer (Project Operating System — 43 Tools across 10 Modules)
Specialized PM algorithms driving the AI development lifecycle:
* **[brain/project_readiness.py](brain/project_readiness.py)**: Evaluates codebase maturity (Levels 0-5), implements onboarding/migration generators (`bootstrap_project`, `adopt_existing_project`, `create_project_workspace`), runs 7-layer health checks (`doctor`), and manages safe resets/archives (8 tools).
* **[brain/orchestrator.py](brain/orchestrator.py)**: Manages developer sprints (`start_session`, `end_session`), suggests conventional commit messages (`prepare_commit`, `commit_changes`), and calculates dashboard recommendations (`next_best_action`, `generate_project_brain`) (6 tools).
* **[brain/todo_engine.py](brain/todo_engine.py)**: Implements structured JSON task backlogs with phase bounds, priority weights, and task dependency blocks (6 tools: `create_task`, `update_task`, `complete_task`, `next_task`, `blocked_tasks`, `list_tasks`).
* **[brain/phase_manager.py](brain/phase_manager.py)**: Scopes current target work through sequential phases (planning, implementation, alpha, beta) and tracks release milestones (7 tools: `get_current_phase`, `set_phase`, `complete_phase`, `next_phase`, `list_phases`, `add_milestone`, `list_milestones`).
* **[brain/prd_manager.py](brain/prd_manager.py)**: Writes, updates, summarizes, and compares Product Requirements Documents (4 tools: `get_prd`, `update_prd`, `summarize_prd`, `compare_work_to_prd`).
* **[brain/requirements.py](brain/requirements.py)**: Extracts specifications into keywords, generates a requirements matrix, and maps requirements implementation percentage and user outcomes (3 tools: `extract_requirements`, `verify_requirements`, `verify_outcome`).
* **[brain/sync_engine.py](brain/sync_engine.py)**: Matches physical files, Git logs, and active branch names to automated tasks, compiling reality verification confidence dossiers and health scores (3 tools: `sync_workspace`, `verify_work`, `project_dashboard`).
* **[brain/handoff_engine.py](brain/handoff_engine.py)**: Formulates session summaries into files under `.project_brain/handoffs/` for seamless model transitions (3 tools: `generate_handoff`, `get_last_handoff`, `list_handoffs`).
* **[brain/guardian.py](brain/guardian.py)**: Enforces technology constraints by scanning imports against forbidden technologies (1 tool: `validate_architecture`).
* **[brain/dependency.py](brain/dependency.py)**: Parses language imports to construct dependency graphs and conducts downstream impact analysis (2 tools: `build_dependency_graph`, `impact_analysis`).

---

## 🛠️ Developer Setup & Implementation Guide

### 1. Clone & Environment Setup
Clone the repository and set up a virtual environment using `uv` (recommended) or standard `venv`:

```bash
# Clone the repository
git clone https://github.com/pranjal2410719/dev-mcp.git
cd dev-mcp

# Setup environment via uv (recommended for speed)
uv venv
source .venv/bin/activate
uv pip install -e .

# OR using standard python venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Standard Code Conventions
* **Typing:** Fully-typed python signatures are required. Enable type annotations at module scopes.
* **Imports:** Sort imports alphabetically. Brain submodules must use absolute module references (e.g., `from app import mcp`, `from security import validate_path`).
* **Error Handling:** Never swallow exceptions. Standardize logs, raise specific exceptions (like `FileNotFoundError` or `ValueError`), and print detailed error logs.
* **Docstrings:** Docstrings must be clean, descriptive, and list all parameters and return types. **Important:** FastMCP uses your python function docstrings and type hints to dynamically compile the JSON schema definitions sent to AI clients. Keep them comprehensive!

### 3. How to Register a New Tool
To register a new tool, define it within a module and annotate it using the `@mcp.tool` decorator:

```python
# In tools/my_helper.py

from app import mcp
from security import validate_path

@mcp.tool(description="A helpful description detailing what this tool does.")
def calculate_something(param1: str, path: str = ".") -> str:
    """Calculate something useful in a validated directory.

    Args:
        param1: Clarifying parameter.
        path: Path to validate.
    """
    valid_path = validate_path(path)
    # Perform logic...
    return "Result summary"
```

Next, register your module by importing it inside `server.py` so it initializes during server boot:
```python
# In server.py
import tools.my_helper  # noqa: F401
```

### 4. Running the Test Suite & Validation Pipeline
Make sure to validate your changes before pushing them. The repository includes unit tests for v2 features (Workspace Lock, Safety Modes, Command Blocklist) and an E2E accuracy validation pipeline that simulates onboarding, PRD requirements tracing, Git workflow commits, and sync engines:

```bash
# Run all unit and integration tests via unittest
.venv/bin/python -m unittest discover -s tests -p "*.py" -v

# Or run individual test suites
.venv/bin/python -m unittest tests/test_v2_features.py
.venv/bin/python -m unittest tests/validate_mcp_flow.py
```

All contributions must pass these tests with zero regressions before submitting a Pull Request.

### 5. Hot Reloading & Client Reconnections
When editing tools or modifying server code, the active stdio pipe cached by your AI Client (e.g., Cursor, Claude Desktop) will go out of sync or throw EOF errors. 

Make sure to restart the MCP server in your client settings to force-load your modifications:
* **Cursor:** Settings → Features → MCP → click **Restart** on `dev-mcp`.
* **Claude Desktop:** Fully **Quit** the app and reopen it.
* **Cline / Roo Code:** Restart the extension or run `/mcp restart dev-mcp`.

---

## 🚀 Contribution Pipeline

1. **Fork the repo** on GitHub.
2. **Create a feature branch** (`git checkout -b feature/amazing-tool`).
3. **Write your feature** and add relevant tests.
4. **Run tests** (`.venv/bin/python -m unittest discover -s tests -p "*.py"`) to ensure all unit tests and validation pipelines pass.
5. **Format your code** using standard formatting guidelines.
6. **Commit changes** using Conventional Commits style (e.g., `feat(search): add fuzzy search matching`).
7. **Submit a Pull Request** to the `main` branch.
