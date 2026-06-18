"""
Phase / Milestone Manager for Project Brain.

Enforces phase-based workflow: only tasks belonging to the current
phase are "allowed".  Prevents scope creep by blocking work on
future phases until the current phase is complete.

Stores data in .project_brain/phases/ and the project context.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app import mcp, load_context as get_context
from security import validate_path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

PHASES_FILE = "phases.json"
MILESTONES_FILE = "milestones.json"


def _phases_path(project_root: str | Path) -> Path:
    r = validate_path(project_root)
    p = r / ".project_brain" / "phases"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_phases(root: str | Path) -> dict:
    p = _phases_path(root) / PHASES_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"phases": [], "current_phase": None}


def _save_phases(root: str | Path, data: dict) -> None:
    p = _phases_path(root) / PHASES_FILE
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_milestones(root: str | Path) -> list[dict]:
    p = _phases_path(root) / MILESTONES_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def _save_milestones(root: str | Path, data: list[dict]) -> None:
    p = _phases_path(root) / MILESTONES_FILE
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="get_current_phase",
    description="Get the current active phase and its status.",
)
def get_current_phase(path: str = ".") -> str:
    """Return the currently active development phase.

    Args:
        path: Project root directory.
    """
    phases = _load_phases(path)
    current = phases.get("current_phase")
    if not current:
        return "No phase set. Use set_phase to define the current phase."

    phase_data = None
    for p in phases.get("phases", []):
        if p.get("name") == current:
            phase_data = p
            break

    if phase_data:
        return (
            f"## Current Phase: {current}\n\n"
            f"**Status:** {phase_data.get('status', 'active')}\n"
            f"**Tracked Tasks:** {len(phase_data.get('tasks', []))}\n"
            f"**Description:** {phase_data.get('description', '')}\n"
        )
    return f"## Current Phase: {current}\n\nStatus: active"


@mcp.tool(
    name="set_phase",
    description="Set the current active development phase. Only tasks in this phase are considered 'in scope'.",
)
def set_phase(phase_name: str, description: str = "", path: str = ".") -> str:
    """Define the current development phase.

    Sets scope for the AI: only work belonging to this phase is allowed.

    Args:
        phase_name: Name of the phase (e.g. 'Phase 4 — Activity Creation').
        description: What this phase involves.
        path: Project root directory.
    """
    phases = _load_phases(path)
    phases["current_phase"] = phase_name

    existing = [p for p in phases.get("phases", []) if p.get("name") == phase_name]
    if not existing:
        phases.setdefault("phases", []).append({
            "name": phase_name,
            "description": description,
            "status": "active",
            "started": datetime.now().isoformat(),
            "tasks": [],
        })
    else:
        existing[0]["status"] = "active"

    _save_phases(path, phases)

    ctx = get_context(path)
    ctx.set("project.current_phase", phase_name)

    return f"Phase set to: {phase_name}"


@mcp.tool(
    name="complete_phase",
    description="Mark the current phase as completed and optionally advance to the next phase.",
)
def complete_phase(notes: str = "", path: str = ".") -> str:
    """Mark the current phase as done.

    Args:
        notes: Summary of what was accomplished in this phase.
        path: Project root directory.
    """
    phases = _load_phases(path)
    current = phases.get("current_phase")
    if not current:
        return "No current phase to complete."

    for p in phases.get("phases", []):
        if p.get("name") == current:
            p["status"] = "completed"
            p["completed"] = datetime.now().isoformat()
            if notes:
                p["notes"] = notes
            break

    _save_phases(path, phases)

    ctx = get_context(path)
    ctx.append("decisions", {
        "date": datetime.now().isoformat(),
        "decision": f"Phase completed: {current}",
        "reason": notes or "Phase completed",
    })

    return f"Phase '{current}' marked as completed."


@mcp.tool(
    name="next_phase",
    description="Mark current phase as complete and advance to the next phase in sequence.",
)
def next_phase(phase_name: str, description: str = "", path: str = ".") -> str:
    """Complete current phase and start a new one.

    Args:
        phase_name: Name of the next phase.
        description: What the next phase involves.
        path: Project root directory.
    """
    phases = _load_phases(path)
    current = phases.get("current_phase")
    if current:
        for p in phases.get("phases", []):
            if p.get("name") == current:
                p["status"] = "completed"
                p["completed"] = datetime.now().isoformat()
                break

    phases["current_phase"] = phase_name
    existing = [p for p in phases.get("phases", []) if p.get("name") == phase_name]
    if not existing:
        phases.setdefault("phases", []).append({
            "name": phase_name,
            "description": description,
            "status": "active",
            "started": datetime.now().isoformat(),
            "tasks": [],
        })
    else:
        existing[0]["status"] = "active"

    _save_phases(path, phases)

    ctx = get_context(path)
    ctx.set("project.current_phase", phase_name)

    transitions = f" from '{current}'" if current else ""
    return f"Advanced{transitions} → **{phase_name}**"


@mcp.tool(
    name="list_phases",
    description="List all phases and their status (completed, active, pending).",
)
def list_phases(path: str = ".") -> str:
    """Show all phases with their completion status.

    Args:
        path: Project root directory.
    """
    phases = _load_phases(path)
    current = phases.get("current_phase")
    all_phases = phases.get("phases", [])

    if not all_phases:
        return "No phases defined. Use set_phase to create one."

    lines = ["# Project Phases\n"]
    for p in sorted(all_phases, key=lambda x: x.get("started", "")):
        name = p.get("name", "?")
        status = p.get("status", "pending")
        marker = "🟢" if status == "active" else "✅" if status == "completed" else "⏳"
        is_current = " ← **CURRENT**" if name == current else ""
        lines.append(f"{marker} **{name}** — {status}{is_current}")
        if p.get("description"):
            lines.append(f"   {p['description']}")

    return "\n".join(lines)


@mcp.tool(
    name="add_milestone",
    description="Define a milestone with a target date and associated features.",
)
def add_milestone(name: str, target_date: str = "", features: str = "", path: str = ".") -> str:
    """Register a project milestone.

    Args:
        name: Milestone name (e.g. 'v1.0 Beta').
        target_date: Target completion date.
        features: Comma-separated list of key features for this milestone.
        path: Project root directory.
    """
    milestones = _load_milestones(path)
    entry = {"name": name, "target": target_date or "TBD", "status": "pending"}
    if features:
        entry["features"] = [f.strip() for f in features.split(",")]
    milestones.append(entry)
    _save_milestones(path, milestones)
    return f"Milestone '{name}' added (target: {target_date or 'TBD'})"


@mcp.tool(
    name="list_milestones",
    description="Show all milestones and their status.",
)
def list_milestones(path: str = ".") -> str:
    """Display all project milestones.

    Args:
        path: Project root directory.
    """
    milestones = _load_milestones(path)
    if not milestones:
        return "No milestones defined. Use add_milestone to create one."

    lines = ["# Milestones\n"]
    for m in milestones:
        status = m.get("status", "pending")
        icon = "✅" if status == "completed" else "🔄" if status == "in_progress" else "📋"
        lines.append(f"{icon} **{m.get('name', '?')}** (target: {m.get('target', 'TBD')})")
        for feat in m.get("features", []):
            lines.append(f"  - {feat}")
    return "\n".join(lines)
