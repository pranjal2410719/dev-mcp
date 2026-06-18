"""
PRD (Product Requirements Document) Manager for Project Brain.

Stores, retrieves, and compares work against PRD documents.
Manages: PRD.md, VISION.md, SCOPE.md, REQUIREMENTS.md in .project_brain/prd/
"""

from __future__ import annotations

from pathlib import Path

from app import mcp, load_context as get_context
from security import validate_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _brain_dir(project_root: str | Path) -> Path:
    """Get the .project_brain directory path (creates if missing)."""
    root = validate_path(project_root)
    brain = root / ".project_brain" / "prd"
    brain.mkdir(parents=True, exist_ok=True)
    return brain


def _read_doc(path: Path) -> str:
    """Read a doc file, returning empty string if missing."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _write_doc(path: Path, content: str) -> None:
    """Write content to a doc file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="get_prd",
    description="Retrieve a PRD document (PRD, VISION, SCOPE, REQUIREMENTS). Returns the content of the specified document.",
)
def get_prd(document: str = "PRD", path: str = ".") -> str:
    """Read a stored PRD document.

    Args:
        document: Which document to read — PRD, VISION, SCOPE, or REQUIREMENTS.
        path: Project root directory.
    """
    brain = _brain_dir(path)
    doc_path = brain / f"{document.upper()}.md"
    content = _read_doc(doc_path)
    if not content:
        return f"No {document.upper()}.md found. Use update_prd to create one."
    return content


@mcp.tool(
    name="update_prd",
    description="Create or update a PRD document (PRD, VISION, SCOPE, REQUIREMENTS).",
)
def update_prd(document: str, content: str, path: str = ".") -> str:
    """Write or overwrite a PRD document.

    Args:
        document: Which document to write — PRD, VISION, SCOPE, or REQUIREMENTS.
        content: The full markdown content of the document.
        path: Project root directory.
    """
    brain = _brain_dir(path)
    doc_path = brain / f"{document.upper()}.md"
    _write_doc(doc_path, content)
    return f"Updated {document.upper()}.md ({len(content)} chars)"


@mcp.tool(
    name="summarize_prd",
    description="Summarize key requirements from PRD documents into a concise bullet list.",
)
def summarize_prd(path: str = ".") -> str:
    """Extract key requirements from all PRD documents.

    Args:
        path: Project root directory.
    """
    brain = _brain_dir(path)
    lines = ["# PRD Summary\n"]

    for doc_name in ["PRD", "VISION", "SCOPE", "REQUIREMENTS"]:
        doc_path = brain / f"{doc_name}.md"
        content = _read_doc(doc_path)
        if content:
            parts = [l.strip() for l in content.split("\n") if l.strip()]
            summary_lines = [l for l in parts if not l.startswith("#")][:5]
            if summary_lines:
                lines.append(f"## {doc_name}")
                for sl in summary_lines:
                    lines.append(f"- {sl[:120]}")
                lines.append("")

    return "\n".join(lines) if len(lines) > 2 else "No PRD documents found. Use update_prd to create them."


@mcp.tool(
    name="compare_work_to_prd",
    description="Compare current project context and tasks against PRD requirements to check alignment.",
)
def compare_work_to_prd(path: str = ".") -> str:
    """Check if current work aligns with documented PRD requirements.

    Reads from both the context store and the todo engine for completeness.

    Args:
        path: Project root directory.
    """
    ctx = get_context(path)
    brain = _brain_dir(path)
    root = validate_path(path)

    prd_content = _read_doc(brain / "PRD.md")
    if not prd_content:
        return "No PRD.md found. Define your PRD first with update_prd."

    # Read tasks from todo engine (primary) and context (fallback)
    import json
    todos_file = root / ".project_brain" / "todos" / "active.json"
    if todos_file.exists():
        tasks = json.loads(todos_file.read_text(encoding="utf-8"))
    else:
        tasks = ctx.data.get("active_tasks", [])

    current_phase = ctx.data.get("project", {}).get("current_phase", "Not set")

    return (
        f"## PRD Alignment Report\n\n"
        f"**PRD Document:** Found ({len(prd_content)} chars)\n"
        f"**Current Phase:** {current_phase}\n"
        f"**Active Tasks:** {len(tasks)}\n\n"
        f"### Active Tasks\n" + (
            "\n".join(f"- **{t.get('id', '?')}** — {t.get('title', t.get('description', ''))} [{t.get('status', '')}]"
                      for t in tasks) if tasks else "  No active tasks"
        ) + "\n\n"
        f"### PRD Preview\n{prd_content[:500]}..."
    )
