## 2026-09-08T10:55:01Z

<USER_REQUEST>
You are the Worker for Milestone 3: CLI Guide & Code Comment Alignment.
Your working directory is: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/worker_m3
Your parent orchestrator is: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0

MANDATORY FIRST STEP: Read the authoritative user request at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md
and the project plan at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_orchestrator_2/PROJECT.md

Consult the comprehensive survey audit reports:
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed/handoff.md
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_2_resumed/handoff.md
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_1_resumed/handoff.md

FILE WRITE OWNERSHIP:
You EXCLUSIVELY own and modify:
- /home/dev/Desktop/projects/mcp/dev-mcp/cli.py
- /home/dev/Desktop/projects/mcp/dev-mcp/server.py
Do NOT modify documentation files or other code files.

OBJECTIVES:
1. In `cli.py`:
   - Update docstring (line 10: "all 50+ MCP tools" -> "all 71 MCP tools").
   - Add `("Brain/Ready", "create_project_workspace", "Create isolated project workspace with git")` to the `COMMANDS` list so all 71 tools are documented in the guide.
   - Verify that `len(cli.COMMANDS) == 71` and all 71 FastMCP tools match.
2. In `server.py`:
   - Update stale tool count comments in module docstrings and registration blocks:
     - Update "tools/ 10 existing generic tools" -> "tools/ 28 existing generic tools across 5 modules".
     - Update "brain.todo_engine — 7 task engine tools" -> "brain.todo_engine — 6 task engine tools".
     - Update "brain.orchestrator — 4 orchestration/session tools" -> "brain.orchestrator — 6 orchestration/session tools".
     - Update "brain.project_readiness — 3 project onboarding tools" -> "brain.project_readiness — 8 project onboarding tools".
     - Ensure comments reflect 71 registered tools, 2 resources, and 4 prompts across 15 modules.
3. Verification:
   - Run `.venv/bin/python cli.py --no-interactive --tab commands` to verify clean output.
   - Run `.venv/bin/python -m unittest discover -s tests -p "*.py"` to ensure zero test regressions (8/8 tests pass).
   - Verify Python syntax via `.venv/bin/python -m py_compile cli.py server.py`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

OUTPUTS:
Write your completion report to:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/worker_m3/handoff.md
Include exact diffs of all changes and verified test outputs.
Maintain progress.md in your working directory.
Notify parent orchestrator via send_message when complete.
</USER_REQUEST>
