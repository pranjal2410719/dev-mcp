# 🚀 Release Notes — dev-mcp v2.0.0 (AI Engineering OS)

Welcome to the release notes for **`dev-mcp` v2.0.0**. This release represents a significant architectural shift, transforming `dev-mcp` from a context-management server into a stateful, secure **AI Engineering Operating System** capable of orchestrating multi-agent, design-to-code pipelines.

---

## 🆕 New Features

### 🔒 1. Workspace Lock & Path Jailing
- Implemented strict path validation (`validate_path`) restricting all file read/write operations and command execution contexts inside the active project root directory when safety modes are enabled.
- Prevents models from escaping project directories or accessing operating system paths (such as `/etc` or home dirs).

### ⚙️ 2. Three safety levels (`safe`, `trusted`, `lab`)
- **`safe`** (default): Restricts operations to the project root, blocks system dangerous commands (`sudo`, `dd`, `reboot`, etc.), blocks folder removals (`delete_recursive`), and blocks destructive git checkouts/cleans.
- **`trusted`**: Limits execution to project root, but permits folder deletions and standard Git reset checkouts.
- **`lab`**: Fully disables workspace lock and audits (suited for virtualized sandbox environments).

### 🏗️ 3. Isolated Project Workspace Creator
- Added the `create_project_workspace` tool allowing users to spawn independent workspaces with template structures:
  - `nextjs`: Configured for TypeScript, React, Next.js (App router), Tailwind CSS, with customized initial PRD.
  - `python`: Configured for Python 3.10+, standard libraries, and testing suites.
  - `blank`: Clean starting workspace layout.
- The workspace creation tool automatically initializes Git, bootstraps the Project Brain contexts, sets up the default milestones, and triggers the initial git commit.

### 🎨 4. Open Design Standard Support
- Extended default project context schemas to capture `open_design` metadata block (`design_system`, `prototype_source`, `open_design_project`, `artifact_paths`).
- Updated the context Markdown exporter to render Open Design artifacts and layouts.

---

## 📝 Documentation & Tutorials
- Added specialized integration guides inside `docs/`:
  - **[docs/security.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/security.md)**: Safety modes, jailing paths, and blocked command catalogs.
  - **[docs/workspaces.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/workspaces.md)**: Sibling workspace directory layout and Project Brain isolation.
  - **[docs/open-design.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/open-design.md)**: Design-to-code integrations and Open Design metadata tracking.
  - **[docs/antigravity.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/antigravity.md)**: Connecting the server to the Google DeepMind Antigravity CLI.
  - **[docs/architecture-v2.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/docs/architecture-v2.md)**: v2.0.0 architectural diagrams and execution topologies.

---

## 🛠️ Testing & Verification
- Created a comprehensive test suite `tests/test_v2_features.py` validating safety modes, path traversal blocks, destructive file operations, and template creations.
- Added git sandbox isolation inside tests to prevent running git commands from traversing up and resetting main repository configurations.
- Verified that all unit tests and validation flows pass cleanly.

---

## 🗺️ Roadmap & Future Work (v2.1.0+)
- **Native Open Design Bridge**: Deep design translation pipeline turning Figma/Open Design vector trees directly into customized React/HTML codebases.
- **Dockerized Lab Sandboxing**: Seamlessly executing arbitrary commands inside temporary throwaway Docker containers under the `lab` safety level.
- **Interactive Multi-Agent Orchestrator CLI**: Enhanced keyboard controls and dashboard overlays inside `dev-mcp-guide` to control safety boundaries dynamically.
