# 📁 Workspace Isolation & Directory Structure

This document outlines the multi-workspace architecture of **`dev-mcp` v2.0.0**, designed to isolate project brain states and prevent data leakage across AI-generated codebases.

---

## 🏗️ 1. Isolated Sibling Directory Layout

To build multiple independent projects with AI without corrupting your main settings, configure a parent directory containing separate sibling project workspaces:

```text
/path/to/projects/
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
2. **`.project_brain/`**: Holds PRD markdown specifications, requirements indexes (`requirements.json`), phases, milestones, active/completed task backlogs, and session handoffs.

The server's internal context engine dynamically switches state based on the path of the tool executing:
- When a tool (e.g., `list_tasks(path="...")` or `get_context(path="...")`) is invoked, `app.load_context(target_path)` validates the path and compares the target root with the active cached `_project_context`.
- If the target root differs, the previous cached context is evicted and a new `ProjectContext` is loaded for the target workspace.
- This ensures complete multi-tenant workspace isolation without cross-project state leakage.

---

## 🛠️ 3. Workspace Creation Flow

To spawn a new isolated workspace dynamically, call the `create_project_workspace` tool (one of the 71 registered tools in `dev-mcp`):
```python
create_project_workspace(name="saas-dashboard", template="nextjs", path="./workspaces")
```

Available templates:
- **`blank`** (default): Generic clean workspace structure.
- **`nextjs`**: Pre-configured for Next.js App Router, TypeScript, React, and Tailwind CSS.
- **`python`**: Pre-configured for Python 3.10+, virtual environments, and unittest/pytest workflows.

This triggers the following sequential actions:
1. Validates that the target directory does not already exist with content (using stack-inspection security bypass to permit creating parent/sibling directories outside current project root).
2. Creates the target directory (e.g. `workspaces/saas-dashboard`).
3. Runs `git init -b main` to establish an isolated Git repository.
4. Generates `.project-context.json` pre-configured for the chosen template.
5. Bootstraps `.project_brain/` directory structure, a default `config.yaml` (`safety_mode: safe`), template PRD, Phase 1 milestone, and initial audit tasks.
6. Stages all created files and runs an initial `git commit` to mark the clean workspace baseline.
