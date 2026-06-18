"""
Project context management tools for dev-mcp.

Provides: init_context, get_context, update_context, add_to_context_list,
          add_key_file, add_task, add_decision, export_context_markdown,
          remove_context_item, reset_context, project_info
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from app import mcp, load_context as get_context, set_context
from context import ProjectContext, detect_and_init_context
from security import validate_path


@mcp.tool(description="Initialize or auto-detect project context. Scans project files to detect tech stack, languages, and frameworks.")
def init_context(path: str = ".") -> str:
    """Auto-detect project information and create/update the project context file.

    Scans the project directory for config files (package.json, pyproject.toml,
    Cargo.toml, etc.) and populates the tech stack automatically.

    Args:
        path: Project root directory.
    """
    root = validate_path(path)
    ctx = detect_and_init_context(str(root))
    set_context(ctx)
    return (
        f"Context initialized at {ctx.path}\n\n"
        f"Project: {ctx.get('project.name', 'Unnamed')}\n"
        f"Languages: {', '.join(ctx.get('tech_stack.languages', []))}\n"
        f"Frameworks: {', '.join(ctx.get('tech_stack.frameworks', []))}\n"
        f"Tools: {', '.join(ctx.get('tech_stack.tools', []))}\n"
        f"Key files tracked: {len(ctx.get('key_files', []))}\n"
        f"Tasks tracked: {len(ctx.get('active_tasks', []))}\n"
    )


@mcp.tool(name="get_context", description="Get the full project context as formatted text. Optionally filter by dot path (e.g. 'tech_stack.languages').")
def get_context_tool(dot_path: str = "", path: str = ".") -> str:
    """Retrieve project context information.

    Args:
        dot_path: Optional dot-notation path to get a specific field
                  (e.g. 'project.name', 'tech_stack.languages').
                  Leave empty to get the entire context.
        path: Project root directory.
    """
    ctx = get_context(path)
    if dot_path:
        val = ctx.get(dot_path)
        if isinstance(val, list):
            return "\n".join(f"- {item}" for item in val)
        if isinstance(val, dict):
            return "\n".join(f"  {k}: {v}" for k, v in val.items())
        return str(val) if val else f"Key '{dot_path}' not found"
    return json.dumps(ctx.data, indent=2)


@mcp.tool(description="Update a specific field in the project context using dot notation (e.g. 'project.description', 'conventions.code_style').")
def update_context(dot_path: str, value: str, path: str = ".") -> str:
    """Set a field in the project context.

    Supports nested paths: 'project.description', 'tech_stack.languages',
    'conventions.code_style', 'architecture.overview', etc.

    For list fields, use the add_to_list tool instead.

    Args:
        dot_path: Dot-notation path to the field (e.g. 'project.description').
        value: The value to set.
        path: Project root directory.
    """
    ctx = get_context(path)
    return ctx.set(dot_path, value)


@mcp.tool(description="Add an item to a list field in the context (e.g. tech_stack.languages, key_files, active_tasks, goals).")
def add_to_context_list(dot_path: str, item: str, path: str = ".") -> str:
    """Add an item to a list in the project context.

    For simple lists pass the item as a string.  For complex items
    (key_files, active_tasks, decisions) pass a JSON string.

    Args:
        dot_path: Path to the list field.
        item: Item to add (string, or JSON for complex items).
        path: Project root directory.
    """
    ctx = get_context(path)
    try:
        parsed = json.loads(item)
    except (json.JSONDecodeError, TypeError):
        parsed = item
    return ctx.append(dot_path, parsed)


@mcp.tool(description="Register a key file with its purpose in the project context.")
def add_key_file(file_path: str, purpose: str, details: str = "", root_path: str = ".") -> str:
    """Add a file to the key files registry.

    Args:
        file_path: Path to the file (relative to project root).
        purpose: What this file does (one sentence).
        details: Optional extended notes about the file.
        root_path: Project root directory.
    """
    ctx = get_context(root_path)
    entry = {"path": file_path, "purpose": purpose}
    if details:
        entry["details"] = details
    return ctx.append("key_files", entry)


@mcp.tool(description="Add an active task to the project context.")
def add_task(task_id: str, description: str, status: str = "pending", branch: str = "", notes: str = "", path: str = ".") -> str:
    """Track an active task in the project context.

    Args:
        task_id: Unique identifier (e.g. 'TASK-1', 'feat-auth').
        description: What needs to be done.
        status: One of: pending, in_progress, blocked, completed.
        branch: Optional git branch name.
        notes: Optional notes.
        path: Project root directory.
    """
    ctx = get_context(path)
    entry = {"id": task_id, "description": description, "status": status}
    if branch:
        entry["branch"] = branch
    if notes:
        entry["notes"] = notes
    return ctx.append("active_tasks", entry)


@mcp.tool(description="Log an architecture decision record (ADR) in the project context.")
def add_decision(decision: str, reason: str, alternatives: str = "", path: str = ".") -> str:
    """Record an important architectural decision.

    Args:
        decision: What was decided.
        reason: Why this decision was made.
        alternatives: Other options that were considered.
        path: Project root directory.
    """
    ctx = get_context(path)
    entry = {
        "date": date.today().isoformat(),
        "decision": decision,
        "reason": reason,
    }
    if alternatives:
        entry["alternatives"] = [a.strip() for a in alternatives.split(",")]
    return ctx.append("decisions", entry)


@mcp.tool(description="Export the project context as a Markdown document for sharing with other LLMs and AI tools.")
def export_context_markdown(path: str = ".") -> str:
    """Export full project context as a formatted Markdown file.

    Creates a ``.project-context.md`` file that can be uploaded to other LLMs,
    shared with team members, or used as system context.

    Args:
        path: Project root directory.
    """
    ctx = get_context(path)
    md = ctx.to_markdown()
    md_path = ctx.path.with_suffix(".md")
    md_path.write_text(md, encoding="utf-8")
    return f"Context exported to {md_path}\n\nPreview:\n\n{md[:2000]}"


@mcp.tool(description="Remove an item from a list in the project context by index.")
def remove_context_item(dot_path: str, index: int, path: str = ".") -> str:
    """Remove an item from a list by its index.

    Args:
        dot_path: Path to the list (e.g. 'active_tasks', 'key_files').
        index: Zero-based index of the item to remove.
        path: Project root directory.
    """
    ctx = get_context(path)
    return ctx.remove_from(dot_path, index)


@mcp.tool(description="Reset the project context to default values (clears all data).")
def reset_context(path: str = ".") -> str:
    """Wipe all stored project context and start fresh.

    Args:
        path: Project root directory.
    """
    ctx = get_context(path)
    return ctx.reset()


@mcp.tool(description="Get information about the current project environment.")
def project_info(path: str = ".") -> str:
    """Return metadata about the project: language, framework detection, file count, etc.

    Args:
        path: Project root directory.
    """
    p = validate_path(path)
    lines = [f"Project root: {p}", ""]

    # Detect project type
    files = list(p.iterdir())
    names = {f.name for f in files}

    if "package.json" in names:
        lines.append("Detected: Node.js / JavaScript / TypeScript project")
    if "pyproject.toml" in names or "requirements.txt" in names:
        lines.append("Detected: Python project")
    if "Cargo.toml" in names:
        lines.append("Detected: Rust project")
    if "go.mod" in names:
        lines.append("Detected: Go project")
    if "Gemfile" in names:
        lines.append("Detected: Ruby project")
    if "Makefile" in names:
        lines.append("Has Makefile")
    if "Dockerfile" in names:
        lines.append("Has Dockerfile")

    # Count files
    total_files = 0
    total_dirs = 0
    for root, dirs, fnames in os.walk(str(p)):
        if ".git" in dirs:
            dirs.remove(".git")
        total_dirs += len(dirs)
        total_files += len(fnames)

    lines.append("")
    lines.append(f"Total files: {total_files:,}")
    lines.append(f"Total directories: {total_dirs:,}")

    # Git info
    git_dir = p / ".git"
    lines.append("Git repository: yes" if git_dir.is_dir() else "Git repository: no")

    # Context info
    ctx_path = p / ProjectContext.FILE_NAME
    if ctx_path.exists():
        lines.append(f"Project context: yes ({ctx_path.name})")
    else:
        lines.append("Project context: not initialized (run init_context)")

    return "\n".join(lines)
