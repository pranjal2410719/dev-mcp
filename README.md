# 🧠 dev-mcp: AI Engineering Operating System

`dev-mcp` is a custom **Model Context Protocol (MCP)** server that turns your AI assistants (Claude, Cursor, Gemini, Cline, Roo Code, Windsurf) into active **Technical Project Managers**. 

Rather than treating the AI as a stateless code generator, `dev-mcp` establishes a persistent **Project Brain** in your workspace directory. This allows you to switch between different AI models and platforms seamlessly without losing context, project goals, tasks, or guidelines.

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

Once connected, guide your AI through **11 Public Core Workflows**. The server handles 53 low-level helper tools under the hood.

```
                         assess_project_readiness()
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼ (If score < 80, empty)                ▼ (If score < 80, legacy)
         bootstrap_project()                     adopt_existing_project()
                 │                                       │
                 └───────────────────┬───────────────────┘
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
2. **Bootstrap or Migrate:**
   - **For new projects:** Run `bootstrap_project()` to write empty directories, project contexts, and milestones.
   - **For existing codebases:** Run `adopt_existing_project()` to scan language extensions, parse the current `README.md` to draft goals, and populate task backlogs.

### Step 2: Set the Scope
Open the generated `.project_brain/prd/PRD.md` file and verify your goals. Run:
1. `extract_requirements` — Extracts requirements and keywords into `requirements.json`.
2. `start_session` — Bootstraps a development sprint and prints a Markdown brief for the model.

### Step 3: Run the Session Loop
During active coding:
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
2. `DEV_MCP_ALLOWED_DIRS` environment variable (colon-separated).
3. The home directory (`$HOME`).

*To restrict directories:*
```bash
export DEV_MCP_ALLOWED_DIRS="/home/user/project1:/home/user/project2"
```

---

## 🧪 Running Validation Tests

Ensure server correctness and E2E workflow consistency by executing the pipeline script:

```bash
.venv/bin/python tests/validate_mcp_flow.py
```

For guidelines on coding conventions, code style, and how to write custom tools for this server, see **[CONTRIBUTING.md](file:///home/dev/Desktop/projects/mcp/dev-mcp/CONTRIBUTING.md)**.
