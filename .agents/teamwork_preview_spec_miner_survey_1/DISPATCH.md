## 2026-09-08T05:29:25Z
You are a Spec Miner subagent for the dev-mcp documentation refresh project.
Working directory: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1
Original request path: /home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md

Read /home/dev/Desktop/projects/mcp/dev-mcp/.agents/ORIGINAL_REQUEST.md first.
Your mission:
1. Locate and inventory all existing documentation files across the repository:
   - README.md, docs/architecture-v2.md, docs/security.md, docs/workspaces.md, docs/user_manual.md, CONTRIBUTING.md, and any others.
2. Perform a line-by-line audit of current documentation vs actual code reality:
   - Broken internal Markdown links (links to non-existent headers or files).
   - Fabricated or hallucinated features, APIs, tools, or CLI flags that do not exist in code.
   - Outdated claims, stale commands, incorrect setup/installation instructions.
   - Version references in docs vs pyproject.toml.
   - Inconsistent terminology across documents.
3. Identify all documentation gaps: what implemented features, tools, or configuration options are completely missing from docs.
4. Check build/lint/test requirements for documentation and code.
5. Maintain progress.md in your working directory with heartbeat timestamps.
6. Write your comprehensive gap analysis and documentation audit into handoff.md in your working directory (/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1/handoff.md).
7. Send a message to your caller when complete referencing your handoff file.
