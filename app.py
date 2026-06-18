"""
Shared application state for dev-mcp.

This module creates the FastMCP instance and holds global state that is
shared across all tool, prompt, and resource modules.

All tool/prompt/resource modules import `mcp` from here to register their
decorators in-place.  `server.py` then imports those modules to trigger
registration, and finally calls ``mcp.run()``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from context import ProjectContext

# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "dev-mcp",
    instructions=(
        "Project management MCP server for building, editing, and customizing "
        "projects with AI. Maintains a persistent project context document that "
        "captures tech stack, architecture, conventions, key files, active "
        "tasks, goals, and architectural decisions. Provides prebuilt prompt "
        "templates for common operations."
    ),
)

# ---------------------------------------------------------------------------
# Shared global state
# ---------------------------------------------------------------------------

# Lazy-initialized project context
_project_context: ProjectContext | None = None


def load_context(project_root: str | Path | None = None) -> ProjectContext:
    """Get (or create) the global project context instance."""
    global _project_context
    if _project_context is None:
        from security import validate_path
        root = validate_path(project_root) if project_root else Path.cwd().resolve()
        _project_context = ProjectContext(root)
    return _project_context


def set_context(ctx: ProjectContext) -> None:
    """Set the global project context (used by init_context tool)."""
    global _project_context
    _project_context = ctx
