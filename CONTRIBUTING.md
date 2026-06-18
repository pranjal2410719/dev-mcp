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

## 📐 Architecture Overview

`dev-mcp` is split into three clean layers: **Core**, **Tools**, and **Brain**.

### 1. Core Layer
- **`app.py`**: Declares the global `FastMCP` instance and context-loading hooks.
- **`context.py`**: Implements `ProjectContext` to manage context reads/writes from `.project-context.json`.
- **`security.py`**: Restricts path traversals by verifying input directories against allowed sandboxes.
- **`server.py`**: Imports other files to register tools/prompts and runs the stdio event loop.

### 2. Tools Layer
Generic, stateless utility wrappers:
- **`file_ops.py`**: Sandboxed file system helper tools (read, write, edit, search).
- **`search.py`**: Ripgrep/Python-fallback text pattern search tool.
- **`terminal.py`**: Shell command exec wrapper with timeout settings.
- **`git_ops.py`**: Simple wrapper around local git commands (status, diff, branch, commit).
- **`context_mgmt.py`**: Simple getters/setters for `.project-context.json`.

### 3. Brain Layer (Project Operating System)
Autonomous state engines orchestrating workflows:
- **`project_readiness.py`**: Readiness grading scoring (Levels 0-5) and onboarding bootstrap engines.
- **`orchestrator.py`**: Session orchestration, target task calculation, and git auto-commit generators.
- **`sync_engine.py`**: Workspace analyzer matching Git reality (branches, commits, diffs) to the task backlog.
- **`requirements.py`**: PRD parsing and keyword trace traceability matrices.
- **`guardian.py`**: Enforcer scanning imports for forbidden architectures/dependencies.
- **`dependency.py`**: BFS parser generating import graphs and calculating blast radius (transitive impacts).

---

## 🛠️ Developer Setup & Implementation Guide

### 1. Clone & Environment Setup
Clone the repository and set up a virtual environment using `uv` (recommended) or `venv`:

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
- **Typing:** Type annotations are required on all functions and decorators (`from __future__ import annotations` is encouraged).
- **Imports:** Place imports alphabetically. All brain imports must be absolute.
- **Error Handling:** Avoid silent failures. Log clear stdout summaries or raise descriptive `ValueError`/`PermissionError` triggers.
- **Docstrings:** All MCP tools must contain descriptive docstrings because FastMCP uses them directly to build descriptions for the LLM client.

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

Next, register your module by importing it inside `server.py`:
```python
# In server.py
import tools.my_helper  # noqa: F401
```

### 4. Running the Validation Pipeline
Make sure to validate your changes before pushing them. The repository includes an E2E accuracy validation script:

```bash
.venv/bin/python tests/validate_mcp_flow.py
```

All contributions must pass the pipeline tests before submitting a Pull Request.

---

## 🚀 Contribution Pipeline

1. **Fork the repo** on GitHub.
2. **Create a feature branch** (`git checkout -b feature/amazing-tool`).
3. **Write your feature** and add relevant tests.
4. **Run `python tests/validate_mcp_flow.py`** to ensure validation passes.
5. **Format your code** using standard formatting guidelines.
6. **Commit changes** using Conventional Commits style (e.g., `feat(search): add fuzzy search matching`).
7. **Submit a Pull Request** to the `main` branch.
