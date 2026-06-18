"""
MCP resource definitions for dev-mcp.

Exposes project context as consumable resources (JSON & Markdown).
"""

from __future__ import annotations

import json

from app import mcp, load_context as get_context


@mcp.resource(
    uri="project://context/json",
    name="Project Context (JSON)",
    description="The full project context document as JSON.",
    mime_type="application/json",
)
def project_context_json_resource() -> str:
    """Expose the project context as JSON."""
    ctx = get_context()
    return json.dumps(ctx.data, indent=2)


@mcp.resource(
    uri="project://context/markdown",
    name="Project Context (Markdown)",
    description="The full project context as a Markdown document for sharing.",
    mime_type="text/markdown",
)
def project_context_markdown_resource() -> str:
    """Expose the project context as Markdown."""
    ctx = get_context()
    return ctx.to_markdown()
