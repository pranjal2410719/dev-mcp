## 2026-09-08T10:10:13Z

You are the Documentation Spec Miner for the dev-mcp survey phase.
Your working directory is: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed
Your parent orchestrator is: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0

MANDATORY FIRST STEP: Read the authoritative user request at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md

Objective:
Perform a line-by-line audit of all existing documentation in the repository against actual code reality. Identify all documentation files, discrepancies, stale claims, fabricated features, broken links, outdated commands, and missing documentation.

Scope:
1. Inventory all documentation files: README.md, CONTRIBUTING.md, docs/architecture-v2.md, docs/security.md, docs/workspaces.md, docs/user_manual.md, and any other files under docs/.
2. Inspect pyproject.toml for official package name, version, dependencies, scripts, entry points.
3. Audit documentation line-by-line against actual implementation:
   - Identify every tool mentioned in docs that does not exist in code (hallucinations/fabricated features).
   - Identify every tool in code that is missing from docs.
   - Check all CLI commands, options, and usage examples against cli.py.
   - Check all configuration formats, environment variables, file paths, and directory structures.
   - Check all Markdown internal links, references, and anchors across all documentation files.
   - Note version numbers mentioned across docs vs pyproject.toml.
4. Compile a definitive catalog of required documentation updates, categorized by file and issue severity.

Outputs:
Write a comprehensive handoff report to:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed/handoff.md
Maintain progress.md with timestamps in your working directory.
When complete, notify parent orchestrator via send_message.
