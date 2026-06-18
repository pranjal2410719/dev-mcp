"""
dev-mcp: A custom MCP server for managing, building, editing, and customizing projects with AI.

This is the entry-point module.  It imports the FastMCP instance from ``app``,
then imports all tool, prompt, resource, and brain modules so they register
their decorators, and finally starts the server.

Module organisation
-------------------
::

    app.py                  FastMCP instance + shared global state
    security.py             Path-validation helpers
    context.py              ProjectContext data-store class
    tools/                  10 existing generic tools
      file_ops.py           8 tools — read, write, edit, delete, list, glob, mkdir
      search.py             1 tool  — ripgrep-based code search
      terminal.py           1 tool  — shell command execution
      git_ops.py            7 tools — status, diff, log, branch, add, commit, create-branch
      context_mgmt.py      11 tools — context CRUD, tasks, decisions, project-info
    brain/                  Project Brain — project operating system
      prd_manager.py        4 tools — get/update/summarize/compare PRD
      phase_manager.py      7 tools — phase lifecycle, milestones
      todo_engine.py        7 tools — structured tasks, deps, priorities
      handoff_engine.py     3 tools — AI handoff generation
    prompts/
      definitions.py        4 prompts — overview, code-review, ADR, feature-plan
    resources/
      definitions.py        2 resources — context as JSON & Markdown
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1.  Import the FastMCP instance so it is available at module scope.
# ---------------------------------------------------------------------------
from app import mcp  # noqa: F401 — activates the instance

# ---------------------------------------------------------------------------
# 2.  Import all tool, prompt, resource, and brain modules.
#     The import itself triggers @mcp.tool / @mcp.prompt / @mcp.resource
#     decorators which register everything on the shared ``mcp`` instance.
# ---------------------------------------------------------------------------
import tools.file_ops          # noqa: F401  — 8 file-operation tools
import tools.search            # noqa: F401  — 1 code-search tool
import tools.terminal          # noqa: F401  — 1 terminal tool
import tools.git_ops           # noqa: F401  — 7 git tools
import tools.context_mgmt      # noqa: F401  — 11 context + utility tools
import brain.prd_manager       # noqa: F401  — 4 PRD tools
import brain.phase_manager     # noqa: F401  — 7 phase/milestone tools
import brain.todo_engine       # noqa: F401  — 7 task engine tools
import brain.handoff_engine    # noqa: F401  — 3 handoff tools
import brain.orchestrator      # noqa: F401  — 4 orchestration/session tools
import brain.guardian          # noqa: F401  – 1 architecture validator
import brain.dependency        # noqa: F401  — 2 dependency graph tools
import brain.sync_engine       # noqa: F401  — 3 reality sync tools
import brain.requirements      # noqa: F401  – 3 requirements traceability tools
import brain.project_readiness # noqa: F401  – 3 project onboarding tools
import prompts.definitions     # noqa: F401  — 4 prompt templates
import resources.definitions   # noqa: F401  — 2 resources

# ---------------------------------------------------------------------------
# 3.  Entry point.
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the dev-mcp server over stdio (default for MCP)."""
    mcp.run()


if __name__ == "__main__":
    main()
