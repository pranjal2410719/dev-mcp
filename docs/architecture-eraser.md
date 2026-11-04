# dev-mcp Architecture Diagram

> AI Engineering Operating System — FastMCP 3.4.2, Python 3.10+, 71 tools across 15 modules + 4 prompts + 2 resources

---

## Eraser DSL

Paste into [app.eraser.io](https://app.eraser.io) → New File → Cloud Architecture Diagram

```
// dev-mcp Architecture — Eraser Cloud Architecture Diagram

// ─── AI Clients ────────────────────────────────────────────────────────
Antigravity [icon: googlecloud-ai-platform, color: purple]
Claude Code [icon: terminal, color: orange]
Cursor [icon: code, color: blue]
VS Code [icon: code, color: blue]
Kiro [icon: terminal, color: gray]
Codex [icon: terminal, color: gray]

// ─── MCP Transport ─────────────────────────────────────────────────────
MCP stdio [icon: network, color: yellow]

// ─── Entry Point ───────────────────────────────────────────────────────
server.py [icon: python, color: blue]

// ─── FastMCP Core ──────────────────────────────────────────────────────
FastMCP [icon: server, color: blue, label: "FastMCP 3.4.2 (app.py)"]
Security [icon: lock, color: red, label: "security.py — Path Whitelist\nDEV_MCP_ALLOWED_DIRS\nsafe / trusted / lab modes"]
ProjectContext [icon: database, color: green, label: "context.py — ProjectContext\nIdentity, Tech Stack, Architecture\nConventions, Key Files, Tasks, Goals, Decisions"]

// ─── Tools Layer ───────────────────────────────────────────────────────
FileOps [icon: files, color: blue, label: "file_ops.py (8 tools)\nread_file, write_file, edit_file\ndelete_path, delete_recursive\nlist_directory, glob_files, create_directory"]
Search [icon: search, color: blue, label: "search.py (1 tool)\nsearch_code — ripgrep"]
Terminal [icon: terminal, color: blue, label: "terminal.py (1 tool)\nrun_command — subprocess + timeout"]
GitOps [icon: git, color: orange, label: "git_ops.py (7 tools)\ngit_status, git_diff, git_log, git_branch\ngit_add, git_commit, git_create_branch"]
ContextMgmt [icon: settings, color: green, label: "context_mgmt.py (11 tools)\ninit_context, get_context, update_context\nadd_to_context_list, add_key_file, add_task\nadd_decision, export_context_markdown\nremove_context_item, reset_context, project_info"]

// ─── Brain Layer ───────────────────────────────────────────────────────
PRDManager [icon: file-text, color: purple, label: "prd_manager.py (4 tools)\nget_prd, update_prd, summarize_prd\ncompare_work_to_prd"]
PhaseManager [icon: clock, color: purple, label: "phase_manager.py (7 tools)\nget_current_phase, set_phase, complete_phase\nnext_phase, list_phases\nadd_milestone, list_milestones"]
TodoEngine [icon: check-square, color: purple, label: "todo_engine.py (6 tools)\ncreate_task, update_task, complete_task\nnext_task, blocked_tasks, list_tasks"]
HandoffEngine [icon: share-2, color: purple, label: "handoff_engine.py (3 tools)\ngenerate_handoff, get_last_handoff\nlist_handoffs"]
Orchestrator [icon: cpu, color: purple, label: "orchestrator.py (6 tools)\ngenerate_project_brain, next_best_action\nstart_session, end_session\nprepare_commit, commit_changes"]
Guardian [icon: shield, color: red, label: "guardian.py (1 tool)\nvalidate_architecture"]
Dependency [icon: git-merge, color: orange, label: "dependency.py (2 tools)\nbuild_dependency_graph, impact_analysis"]
SyncEngine [icon: refresh-cw, color: orange, label: "sync_engine.py (3 tools)\nverify_work, sync_workspace\nproject_dashboard"]
Requirements [icon: clipboard, color: green, label: "requirements.py (3 tools)\nextract_requirements, verify_requirements\nverify_outcome"]
Readiness [icon: check-circle, color: green, label: "project_readiness.py (8 tools)\nassess_project_readiness, project_readiness_report\nbootstrap_project, adopt_existing_project\ndoctor, reset_project_brain\narchive_project_brain, create_project_workspace"]

// ─── Prompts + Resources ───────────────────────────────────────────────
Prompts [icon: message-square, color: yellow, label: "prompts/ (4 templates)\nproject-overview, code-review\narchitectural-decision, feature-plan"]
Resources [icon: package, color: yellow, label: "resources/ (2 MCP resources)\nproject://context/json\nproject://context/markdown"]

// ─── Persistence ───────────────────────────────────────────────────────
ProjectBrain [icon: database, color: gray, label: ".project_brain/ (per workspace)\ncontext.json\nprd/: PRD.md, VISION.md, SCOPE.md\nphases/: phases.json\ntodos/: active.json, completed.json\nhandoffs/: AI session summaries"]
DiskFS [icon: hard-drive, color: gray, label: "Project Workspace\n(DEV_MCP_ALLOWED_DIRS)"]

// ─── Connections ──────────────────────────────────────────────────────
Antigravity > MCP stdio
Claude Code > MCP stdio
Cursor > MCP stdio
VS Code > MCP stdio
Kiro > MCP stdio
Codex > MCP stdio

MCP stdio > server.py
server.py > FastMCP
FastMCP > Security: validates paths
FastMCP > ProjectContext

FastMCP > FileOps
FastMCP > Search
FastMCP > Terminal
FastMCP > GitOps
FastMCP > ContextMgmt

FastMCP > PRDManager
FastMCP > PhaseManager
FastMCP > TodoEngine
FastMCP > HandoffEngine
FastMCP > Orchestrator
FastMCP > Guardian
FastMCP > Dependency
FastMCP > SyncEngine
FastMCP > Requirements
FastMCP > Readiness

FastMCP > Prompts
FastMCP > Resources

Security > DiskFS
FileOps > DiskFS
Terminal > DiskFS
GitOps > DiskFS

PRDManager > ProjectBrain
PhaseManager > ProjectBrain
TodoEngine > ProjectBrain
HandoffEngine > ProjectBrain
Orchestrator > ProjectBrain
Orchestrator < TodoEngine
Orchestrator < PhaseManager
Orchestrator < HandoffEngine

ProjectContext <> ProjectBrain: context.json
Resources < ProjectContext
```

---

## Tool Count

| Layer | Modules | Tools |
|-------|---------|-------|
| Tools | 5 | 28 |
| Brain | 10 | 43 |
| **Total Tools** | **15** | **71** |
| Prompts | 1 | 4 |
| Resources | 1 | 2 |
| **Total Capabilities** | **17** | **77** |

---

## Data Flow

```
AI Client → MCP stdio → server.py → FastMCP → security.py (path check)
  → tool module → ProjectContext / .project_brain/ / project files
  ← response ← stdio ← AI Client
```

---

## Render with Eraser API (once you have an API key)

```bash
# Set up API key
eraser-setup auth

# Then ask AGY:
# "Use Eraser MCP to generate an architecture diagram from the DSL in docs/architecture-eraser.md"
```

Or use the render API directly:
```bash
curl -X POST https://app.eraser.io/api/render/prompt \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Generate a cloud architecture diagram for dev-mcp: AI clients connect via MCP stdio to server.py which routes through FastMCP core (security + ProjectContext) to 15 tool/brain modules. Brain modules persist state in .project_brain/. Tools: 28 in file_ops/search/terminal/git_ops/context_mgmt. Brain: 43 in prd_manager/phase_manager/todo_engine/handoff_engine/orchestrator/guardian/dependency/sync_engine/requirements/project_readiness. Prompts: 4 in prompts/. Resources: 2 in resources/.",
    "diagramType": "cloud-architecture-diagram",
    "theme": "dark",
    "imageQuality": 3,
    "fileOptions": { "create": true, "linkAccess": "publicly-viewable" }
  }'
```
