## 2026-09-08T10:26:20Z
<USER_REQUEST>
You are the Worker for Milestone 1: Core Documentation Refresh.
Your working directory is: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/worker_m1
Your parent orchestrator is: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0

MANDATORY FIRST STEP: Read the authoritative user request at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md
and the project plan at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_orchestrator_2/PROJECT.md

Consult the comprehensive survey audit reports for exact file locations, line numbers, and details:
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed/handoff.md
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_2_resumed/handoff.md
- /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_1_resumed/handoff.md

FILE WRITE OWNERSHIP:
You EXCLUSIVELY own and modify these three files:
- /home/dev/Desktop/projects/mcp/dev-mcp/README.md
- /home/dev/Desktop/projects/mcp/dev-mcp/CONTRIBUTING.md
- /home/dev/Desktop/projects/mcp/dev-mcp/docs/user_manual.md
Do NOT modify other files in this milestone.

OBJECTIVES:
1. Tool Count: Update all references claiming "70 tools" to "71 tools" across README.md and docs/user_manual.md.
2. Add `create_project_workspace`: Add full parameter signatures and descriptions for `create_project_workspace` to the tool reference tables in both README.md and docs/user_manual.md (Section 1 / 6.A under Brain/Project Readiness).
3. Correct `update_task`: Remove the hallucinated parameters (`description`, `phase`, `depends_on`) from README.md:283 and docs/user_manual.md:247. The true signature is `task_id: str, status: str = "", priority: str = "", title: str = "", path: str = "."`.
4. Correct `list_tasks`: Add `priority: str = ""` to the parameter tables in README.md:287 and docs/user_manual.md:251.
5. Fix Broken Links: Replace all 33 machine-specific `file:///home/dev/Desktop/projects/mcp/dev-mcp/...` URLs in README.md (9 instances), CONTRIBUTING.md (19 instances), and docs/user_manual.md (5 instances) with clean, portable relative Markdown links.
6. Fix Security Sandbox Documentation: In README.md (around line 425) and docs/user_manual.md (around line 383), replace the obsolete sandbox description (which claimed $HOME was allowed) with the actual v2 security architecture: Workspace Lock (strict jailing to active project root in `safe` and `trusted` modes), stack-inspected onboarding bypass (`bootstrap_project`, `create_project_workspace`, `adopt_existing_project`), and the 3 safety modes (`safe`, `trusted`, `lab`).
7. Sample config.yaml: Update the sample `.project_brain/config.yaml` in README.md and docs/user_manual.md to include `safety_mode: safe`.
8. Portable paths: Replace hardcoded developer paths (`/home/dev/...`) in examples with generic placeholders (`/path/to/dev-mcp` or `~/projects/my-app`).
9. CONTRIBUTING.md updates: Update architectural diagram/layers to reflect all 15 modules and 71 tools; update security controller description; update test running instructions to include both `test_v2_features.py` and `validate_mcp_flow.py` via `python -m unittest`.
10. Run tests and link checks: Run `python -m unittest discover -s tests -p "*.py"` using `.venv/bin/python` to verify zero test regressions. Verify that no broken links or `file:///` URLs remain in your owned files.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

OUTPUTS:
Write your completion report to:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/worker_m1/handoff.md
Include exact diffs/summaries of all changes and verified test/check outputs.
Maintain progress.md in your working directory.
Notify parent orchestrator via send_message when complete.
</USER_REQUEST>
