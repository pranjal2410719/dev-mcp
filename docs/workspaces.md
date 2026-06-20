# 📁 Workspace Isolation & Directory Structure

This document outlines the multi-workspace architecture of **`dev-mcp` v2.0.0**, designed to isolate project brain states and prevent data leakage across AI-generated codebases.

---

## 🏗️ 1. Isolated Sibling Directory Layout

To build multiple independent projects with AI without corrupting your main settings, configure a parent directory containing separate sibling project workspaces:

```text
/home/dev/Desktop/projects/
├── dev-mcp/                     # Central AI Engineering OS codebase
├── open-design/                 # Design system tools workspace
└── workspaces/                  # Root folder for generated projects
    ├── saas-dashboard/          # Isolated Next.js project 1
    │   ├── .project-context.json
    │   └── .project_brain/
    └── python-utility/          # Isolated Python project 2
        ├── .project-context.json
        └── .project_brain/
```

---

## 🔒 2. Project Brain Partitioning

Each workspace directory initialized by `dev-mcp` has its own isolated Project Brain:
1. **`.project-context.json`**: Captures tech stack, key file directories, architecture conventions, active tasks, and Open Design metadata.
2. **`.project_brain/`**: Holds PRD text specs, requirements indexes, milestones log, and session handoffs.

The server's internal context engine dynamically switches state based on the path of the tool executing:
- When a tool (e.g., `list_tasks(path="...")`) is invoked, the context manager loads/saves data *only* within that target workspace.
- This prevents cross-contaminating project roadmaps and ensures total context isolation.

---

## 🛠️ 3. Workspace Creation Flow

To spawn a new isolated workspace dynamically, run:
```python
create_project_workspace(name="saas-dashboard", template="nextjs", path="./workspaces")
```
This triggers the following sequential actions:
1. Creates directory `workspaces/saas-dashboard`.
2. Runs `git init` to isolate version histories.
3. Generates `.project-context.json` pre-configured for the target framework.
4. Generates `.project_brain/` folders, a standard `config.yaml`, milestone stubs, and initial audit tasks.
5. Runs an initial `git commit` to mark the workspace baseline.
