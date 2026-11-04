# Original User Request

## 2026-09-08T05:28:08Z

# Teamwork Project Prompt — Draft

> Status: Step 9 — Final Prompt Ready
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Deeply audit and understand the entire dev‑mcp codebase, then perform a complete documentation refresh that accurately reflects the current implementation, architecture, MCP tools, security model, workspace system, CLI capabilities, Project Brain/orchestration, setup, configuration, development workflow, testing, and extension points.

Working directory: ~/teamwork_projects/dev_mcp_doc_refresh

Integrity mode: development

## Requirements

### R1. Comprehensive codebase audit
Audit the full repository structure, entry points, tool registration, security and workspace models, and tests. Produce a mental model of the architecture and a map of all MCP tools/resources.

### R2. Documentation update
Review and update all markdown documentation files (README.md, docs/architecture‑v2.md, docs/security.md, docs/workspaces.md, docs/user_manual.md, CONTRIBUTING.md, and any other discovered docs) to match the actual code. Fix broken links, outdated claims, inconsistent terminology, incorrect commands, stale file references, and remove any fabricated features.

### R3. Validation and testing
Run the project's test suite, linting, build, and import checks. Verify that updated documentation renders correctly on GitHub, contains no broken internal links, and that version references match pyproject.toml.

### R4. Final report
Generate a detailed report summarizing architecture understanding, documentation changes, discovered issues, validation results, git status, and a recommended commit message. Indicate whether the repository is READY TO PUSH.

## Acceptance Criteria

- [ ] All updated documentation accurately reflects the current implementation with no fabricated APIs or capabilities.
- [ ] No broken internal Markdown links; all file paths and commands referenced exist.
- [ ] Version numbers in docs match the version specified in pyproject.toml.
- [ ] No sensitive information (API keys, passwords, tokens) is introduced.
- [ ] Architecture and security sections correctly describe actual code behavior.
- [ ] Workspace documentation correctly describes resolution, isolation, and safety controls.
- [ ] Installation and setup instructions are reproducible from a clean checkout.
- [ ] All project tests pass, linting succeeds, and the build completes without errors.
- [ ] git status shows only intentional documentation changes.
- [ ] Final report includes all required sections and a clear READY TO PUSH or NOT READY TO PUSH verdict.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*
