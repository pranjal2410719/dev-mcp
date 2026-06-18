"""
Project Context System for dev-mcp.

Manages a structured, persistent context document about the project:
  - Identity, tech stack, architecture, conventions
  - Key files and their purposes
  - Active tasks, goals, and roadmap
  - Exportable/shareable with other LLMs and tools
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Default / Template Schema
# ---------------------------------------------------------------------------

DEFAULT_CONTEXT: dict[str, Any] = {
    "project": {
        "name": "",
        "description": "",
        "version": "0.1.0",
        "created": "",
        "updated": "",
    },
    "tech_stack": {
        "languages": [],
        "frameworks": [],
        "databases": [],
        "tools": [],
        "infrastructure": [],
    },
    "architecture": {
        "overview": "",
        "key_patterns": [],
        "directory_structure": {},
        "rules": {
            "forbidden_technologies": [],
            "required_technologies": []
        }
    },
    "conventions": {
        "code_style": "",
        "naming_conventions": "",
        "git_workflow": "",
        "testing_approach": "",
        "commit_message_style": "",
    },
    "key_files": [
        # { "path": "src/main.py", "purpose": "Entry point", "details": "" }
    ],
    "active_tasks": [
        # { "id": "TASK-1", "description": "...", "status": "in_progress", "branch": "", "notes": "" }
    ],
    "goals": [
        # { "goal": "...", "priority": "high", "status": "pending" }
    ],
    "milestones": [
        # { "name": "v1.0", "target": "2026-07-01", "features": [] }
    ],
    "decisions": [
        # { "date": "2026-06-18", "decision": "...", "reason": "...", "alternatives": [] }
    ],
}


# ---------------------------------------------------------------------------
# Context Store
# ---------------------------------------------------------------------------

class ProjectContext:
    """Manages a project context document stored as JSON in the project root."""

    FILE_NAME = ".project-context.json"

    def __init__(self, project_root: str | Path | None = None) -> None:
        self._root: Path = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        self._path: Path = self._root / self.FILE_NAME
        self._data: dict[str, Any] = {}
        self._load()

    # ---- Persistence -------------------------------------------------------

    def _load(self) -> None:
        """Load context from disk, or initialize with defaults."""
        if self._path.exists():
            try:
                raw = self._path.read_text(encoding="utf-8")
                self._data = json.loads(raw)
            except (json.JSONDecodeError, OSError):
                self._data = dict(DEFAULT_CONTEXT)
        else:
            self._data = dict(DEFAULT_CONTEXT)
        self._ensure_fields()

    def _save(self) -> None:
        """Persist context to disk."""
        self._data["project"]["updated"] = datetime.now().isoformat()
        self._path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _ensure_fields(self) -> None:
        """Ensure all default keys exist (in case context was created by older version)."""
        def deep_merge(base: Any, overlay: Any) -> Any:
            if isinstance(base, dict) and isinstance(overlay, dict):
                merged = dict(base)
                for k, v in overlay.items():
                    merged[k] = deep_merge(base.get(k, {}), v) if isinstance(v, dict) else v
                return merged
            return overlay if overlay is not None else base
        self._data = deep_merge(DEFAULT_CONTEXT, self._data)

    # ---- Accessors ---------------------------------------------------------

    @property
    def path(self) -> Path:
        return self._path

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    def exists(self) -> bool:
        """Check if a context file already exists on disk."""
        return self._path.exists()

    def get(self, dot_path: str, default: Any = "") -> Any:
        """Get a value using dot notation, e.g. 'project.name'."""
        parts = dot_path.split(".")
        val: Any = self._data
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
                if val is None:
                    return default
            else:
                return default
        return val if val is not None else default

    def set(self, dot_path: str, value: Any) -> str:
        """Set a value using dot notation, creating intermediate keys if needed."""
        parts = dot_path.split(".")
        target = self._data
        for part in parts[:-1]:
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value
        self._save()
        return f"Updated '{dot_path}'"

    def append(self, dot_path: str, item: Any) -> str:
        """Append an item to a list at *dot_path*."""
        lst = self.get(dot_path, [])
        if not isinstance(lst, list):
            return f"Error: '{dot_path}' is not a list"
        lst.append(item)
        self.set(dot_path, lst)
        return f"Appended item to '{dot_path}'"

    def remove_from(self, dot_path: str, index: int) -> str:
        """Remove an item by index from a list at *dot_path*."""
        lst = self.get(dot_path, [])
        if not isinstance(lst, list):
            return f"Error: '{dot_path}' is not a list"
        if 0 <= index < len(lst):
            removed = lst.pop(index)
            self.set(dot_path, lst)
            return f"Removed item {index} from '{dot_path}'"
        return f"Error: index {index} out of range"

    def reset(self) -> str:
        """Reset context to defaults (wipes all data)."""
        self._data = dict(DEFAULT_CONTEXT)
        self._data["project"]["created"] = datetime.now().isoformat()
        self._save()
        return "Context reset to defaults"

    def to_markdown(self) -> str:
        """Export the full context as a formatted Markdown document for sharing with LLMs."""
        d = self._data
        lines: list[str] = [
            f"# Project Context: {d.get('project', {}).get('name', 'Unnamed')}",
            "",
        ]

        # Project info
        proj = d.get("project", {})
        lines.append("## Project Overview")
        lines.append(f"- **Name:** {proj.get('name', 'N/A')}")
        lines.append(f"- **Description:** {proj.get('description', 'N/A')}")
        lines.append(f"- **Version:** {proj.get('version', 'N/A')}")
        lines.append("")

        # Tech stack
        tech = d.get("tech_stack", {})
        lines.append("## Tech Stack")
        for category, items in tech.items():
            if items:
                lines.append(f"- **{category.replace('_', ' ').title()}:** {', '.join(items)}")
        lines.append("")

        # Architecture
        arch = d.get("architecture", {})
        lines.append("## Architecture")
        if arch.get("overview"):
            lines.append(arch["overview"])
            lines.append("")
        if arch.get("key_patterns"):
            lines.append("### Key Patterns")
            for pat in arch["key_patterns"]:
                lines.append(f"- {pat}")
            lines.append("")
        if arch.get("directory_structure"):
            lines.append("### Directory Structure")
            lines.append("```")
            lines.extend(_format_directory_tree(arch["directory_structure"]))
            lines.append("```")
            lines.append("")

        # Conventions
        conv = d.get("conventions", {})
        has_conv = any(v for v in conv.values())
        if has_conv:
            lines.append("## Conventions")
            for key, val in conv.items():
                if val:
                    lines.append(f"- **{key.replace('_', ' ').title()}:** {val}")
            lines.append("")

        # Key files
        kf = d.get("key_files", [])
        if kf:
            lines.append("## Key Files")
            for entry in kf:
                lines.append(f"- **{entry.get('path', '?')}** — {entry.get('purpose', '')}")
                if entry.get("details"):
                    lines.append(f"  - {entry['details']}")
            lines.append("")

        # Active tasks
        tasks = d.get("active_tasks", [])
        if tasks:
            lines.append("## Active Tasks")
            for t in tasks:
                lines.append(f"- [{t.get('status', '?')}] **{t.get('id', '?')}:** {t.get('description', '')}")
                if t.get("branch"):
                    lines.append(f"  - Branch: `{t['branch']}`")
                if t.get("notes"):
                    lines.append(f"  - Notes: {t['notes']}")
            lines.append("")

        # Goals
        goals = d.get("goals", [])
        if goals:
            lines.append("## Goals & Priorities")
            for g in goals:
                status_icon = "✅" if g.get("status") == "completed" else "🔄" if g.get("status") == "in_progress" else "📋"
                lines.append(f"- {status_icon} **[ {g.get('priority', 'medium')} ]** {g.get('goal', '')}")
            lines.append("")

        # Milestones
        ms = d.get("milestones", [])
        if ms:
            lines.append("## Milestones")
            for m in ms:
                lines.append(f"- **{m.get('name', '')}** (target: {m.get('target', 'TBD')})")
                for feat in m.get("features", []):
                    lines.append(f"  - {feat}")
            lines.append("")

        # Architectural decisions
        decisions = d.get("decisions", [])
        if decisions:
            lines.append("## Architecture Decisions")
            for dec in decisions:
                lines.append(f"- **{dec.get('date', '')}** — {dec.get('decision', '')}")
                if dec.get("reason"):
                    lines.append(f"  - Why: {dec['reason']}")
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_directory_tree(structure: dict, indent: int = 0) -> list[str]:
    """Recursively format a directory structure dict into an ASCII tree."""
    lines: list[str] = []
    for key, val in structure.items():
        prefix = "  " * indent
        if isinstance(val, dict):
            lines.append(f"{prefix}{key}/")
            lines.extend(_format_directory_tree(val, indent + 1))
        else:
            lines.append(f"{prefix}{key}  # {val}")
    return lines


def detect_and_init_context(project_root: str | Path) -> ProjectContext:
    """Auto-detect project info and initialize context."""
    ctx = ProjectContext(project_root)
    root = Path(project_root).resolve()

    # Auto-fill project name from directory
    if not ctx.get("project.name"):
        ctx.set("project.name", root.name)

    # Auto-detect tech stack
    names = {f.name for f in root.iterdir()}

    languages = set()
    frameworks = set()
    tools = set()

    if "package.json" in names:
        languages.add("JavaScript")
        try:
            pkg = json.loads((root / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if any("react" in k.lower() for k in deps):
                frameworks.add("React")
            if any("vue" in k.lower() for k in deps):
                frameworks.add("Vue")
            if any("next" in k.lower() for k in deps):
                frameworks.add("Next.js")
            if any("typescript" in k.lower() for k in deps):
                languages.add("TypeScript")
        except (json.JSONDecodeError, OSError):
            pass

    if "pyproject.toml" in names or "requirements.txt" in names:
        languages.add("Python")
        if "pyproject.toml" in names:
            tools.add("uv / pip")

    if "Cargo.toml" in names:
        languages.add("Rust")

    if "go.mod" in names:
        languages.add("Go")

    if "Gemfile" in names:
        languages.add("Ruby")

    if "Makefile" in names:
        tools.add("Make")

    if "Dockerfile" in names or root.joinpath("docker-compose.yml").exists():
        tools.add("Docker")

    if root.joinpath(".github/workflows").exists():
        tools.add("GitHub Actions")

    if "tsconfig.json" in names:
        languages.add("TypeScript")

    existing_langs = set(ctx.get("tech_stack.languages", []))
    existing_fw = set(ctx.get("tech_stack.frameworks", []))
    existing_tools = set(ctx.get("tech_stack.tools", []))

    updated = False
    for lang in languages - existing_langs:
        ctx.append("tech_stack.languages", lang)
        updated = True
    for fw in frameworks - existing_fw:
        ctx.append("tech_stack.frameworks", fw)
        updated = True
    for tool in tools - existing_tools:
        ctx.append("tech_stack.tools", tool)
        updated = True

    if not ctx.get("project.created"):
        ctx.set("project.created", datetime.now().isoformat())
        updated = True

    if updated:
        ctx._save()

    return ctx
