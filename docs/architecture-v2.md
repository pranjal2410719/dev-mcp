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
2. **Command Blocklist**: Heavy regex audits filter command execution to reject relative traversal (`..`), system dangerous utilities (`sudo`, `mkfs`, `dd`, `shutdown`, `reboot`), and user absolute paths outside the workspace.
3. **Safe mode specific**: Blocks recursive deletion (`delete_recursive`), hard git resets (`git reset --hard`), and untracked cleans (`git clean -fd`).
