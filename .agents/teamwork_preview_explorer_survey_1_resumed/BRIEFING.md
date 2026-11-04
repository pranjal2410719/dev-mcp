# BRIEFING — 2026-09-08T10:21:30Z

## Mission
Deeply audit dev-mcp codebase architecture, entry points, core systems, workspace resolution, and test infrastructure for survey phase.

## 🔒 My Identity
- Archetype: explorer
- Roles: architecture audit, entry points analysis, workspace resolution analysis, test infrastructure verification
- Working directory: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_1_resumed
- Original parent: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0
- Milestone: survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Write metadata/reports only to /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_1_resumed
- Evidence-based findings with exact file paths, line numbers, and signatures
- Do not modify project code

## Current Parent
- Conversation ID: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0
- Updated: 2026-09-08T10:20:24Z

## Investigation State
- **Explored paths**: app.py, server.py, cli.py, security.py, context.py, pyproject.toml, .project-context.json, .project_brain/ (config.yaml, phases/, todos/, prd/), tools/ (file_ops.py, search.py, terminal.py, git_ops.py, context_mgmt.py), brain/ (prd_manager.py, phase_manager.py, todo_engine.py, handoff_engine.py, orchestrator.py, guardian.py, dependency.py, sync_engine.py, requirements.py, project_readiness.py), prompts/definitions.py, resources/definitions.py, tests/test_v2_features.py, tests/validate_mcp_flow.py, docs/ (workspaces.md, security.md, architecture-v2.md, user_manual.md), README.md.
- **Key findings**:
  1. Entry points: server:main starts FastMCP server via stdio (non-interactive pipe) or threaded daemon with interactive /dev/tty raw key reader (press ? for cli guide). cli:main runs dev-mcp-guide with Rich UI.
  2. Workspace & Context: dynamic ProjectContext loaded per path; Workspace Lock jailed inside active workspace for 'safe' and 'trusted' modes; safety mode read from .project_brain/config.yaml. create_project_workspace spawns isolated repos with templates.
  3. Test infrastructure: 8 tests across 2 files; all 8 pass (test_v2_features: 7, validate_mcp_flow: 1).
  4. Tool disparity: exactly 71 registered tools (README claims 70, cli.py lists 53).
- **Unexplored areas**: None within scope.

## Key Decisions Made
- Audited test execution via both Python unittest and system pytest with PYTHONPATH.
- Traced exact AST-based tool registration (71 tools, 2 resources, 4 prompts).

## Artifact Index
- DISPATCH.md — Incoming parent tasks and context
- BRIEFING.md — Persistent working memory and identity
- progress.md — Heartbeat and activity log
- handoff.md — Comprehensive 5-component handoff report
