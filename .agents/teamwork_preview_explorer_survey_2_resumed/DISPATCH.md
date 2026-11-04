## 2026-09-08T10:10:13Z

You are the Tools, Security & Project Brain Explorer for the dev-mcp survey phase.
Your working directory is: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_2_resumed
Your parent orchestrator is: 5c72539b-bc38-4a93-8dd0-4732b3ba6da0

MANDATORY FIRST STEP: Read the authoritative user request at:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md

Objective:
Audit all MCP tools, resources, prompts, security model, and Project Brain subsystems in dev-mcp.

Scope:
1. Tool inventory: inspect every file in tools/ and tool registration in server.py and app.py. Document every single MCP tool name, parameters, return types, error handling, and category (filesystem, git, context, project management, brain, etc.).
2. Security & Validation model: inspect security.py and any security checks in tools/ and server.py. Document path traversal protection, command execution sandboxing, allowed commands, workspace root constraints, permission checks, and sensitive data protection.
3. Resources & Prompts: inspect resources/ and prompts/ (or wherever defined). Document all MCP resources (URIs, schemas) and prompts (names, arguments).
4. Project Brain: inspect brain/. Document what Project Brain is, how it stores state, brain commands/tools, migrations, lifecycle.
5. Extension points: Document how new tools, resources, and hooks are added.

Outputs:
Write a comprehensive handoff report to:
/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_2_resumed/handoff.md
Maintain progress.md with timestamps in your working directory.
When complete, notify parent orchestrator via send_message.
