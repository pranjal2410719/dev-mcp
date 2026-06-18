"""
AI Handoff Engine for Project Brain.

Generates session summaries so the next AI session picks up
instantly without re-explaining context.

Every handoff is stored in .project_brain/handoffs/ and also
written as a markdown file that can be shared across any AI tool
(ChatGPT, Claude, Gemini, Cursor, etc.).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app import mcp, load_context as get_context
from security import validate_path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HANDOFFS_DIR = "handoffs"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _handoffs_path(project_root: str | Path) -> Path:
    r = validate_path(project_root)
    p = r / ".project_brain" / HANDOFFS_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_handoff_log(root: str | Path) -> list[dict]:
    p = _handoffs_path(root) / "session-log.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def _save_handoff_log(root: str | Path, log: list[dict]) -> None:
    p = _handoffs_path(root) / "session-log.json"
    p.write_text(json.dumps(log, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="generate_handoff",
    description="Generate a session summary capturing what was done, what's next, and current project state for handoff to another AI.",
)
def generate_handoff(
    session_summary: str = "",
    known_issues: str = "",
    path: str = ".",
) -> str:
    """Create a handoff document so the next AI session has full context.

    Args:
        session_summary: Brief summary of what was accomplished this session.
        known_issues: Any bugs or issues the next session should know about.
        path: Project root directory.
    """
    ctx = get_context(path)
    root = validate_path(path)

    project = ctx.data.get("project", {})
    tech = ctx.data.get("tech_stack", {})
    current_phase = project.get("current_phase", "Not set")

    todos_dir = root / ".project_brain" / "todos"
    active_tasks = []
    if (todos_dir / "active.json").exists():
        active_tasks = json.loads((todos_dir / "active.json").read_text(encoding="utf-8"))
    completed_tasks = []
    if (todos_dir / "completed.json").exists():
        completed_tasks = json.loads((todos_dir / "completed.json").read_text(encoding="utf-8"))

    key_files = ctx.data.get("key_files", [])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_stamp = datetime.now().strftime("%Y-%m-%d")

    md_lines = [
        f"# AI Handoff — {project.get('name', 'Unnamed')}",
        f"**Session Date:** {timestamp}",
        "",
        "## Project State",
        f"- **Phase:** {current_phase}",
        f"- **Tech Stack:** {', '.join(tech.get('languages', []) + tech.get('frameworks', []))}",
        "",
    ]

    if active_tasks:
        md_lines.append("## Active Tasks")
        in_progress = [t for t in active_tasks if t.get("status") == "in_progress"]
        pending = [t for t in active_tasks if t.get("status") == "pending"]
        blocked = [t for t in active_tasks if t.get("status") == "blocked"]

        if in_progress:
            md_lines.append("### In Progress")
            for t in in_progress:
                md_lines.append(f"- **{t.get('id', '?')}** — {t.get('title', '')}")
        if pending:
            md_lines.append("### Pending")
            for t in pending:
                md_lines.append(f"- **{t.get('id', '?')}** — {t.get('title', '')} [{t.get('priority', 'medium')}]")
        if blocked:
            md_lines.append("### Blocked")
            for t in blocked:
                md_lines.append(f"- **{t.get('id', '?')}** — {t.get('title', '')}")
        md_lines.append("")

    if session_summary:
        md_lines.append("## Session Summary")
        md_lines.append(session_summary)
        md_lines.append("")

    completed_in = [t for t in completed_tasks if t.get("completed", "").startswith(date_stamp)]
    if completed_in:
        md_lines.append("## Completed This Session")
        for t in completed_in:
            md_lines.append(f"- **{t.get('id', '?')}** — {t.get('title', '')}")
        md_lines.append("")

    if known_issues:
        md_lines.append("## Known Issues")
        md_lines.append(known_issues)
        md_lines.append("")

    if key_files:
        md_lines.append("## Key Files")
        for f in key_files:
            md_lines.append(f"- {f.get('path', '?')} — {f.get('purpose', '')}")
        md_lines.append("")

    md_lines.append("## Next Task")
    md_lines.append("Run `next_task` to find the highest-priority work item.")
    md_lines.append("")

    handoff_md = "\n".join(md_lines)

    handoffs_dir = _handoffs_path(path)
    md_file = handoffs_dir / f"{date_stamp}.md"
    md_file.write_text(handoff_md, encoding="utf-8")

    log = _load_handoff_log(path)
    log_entry = {
        "timestamp": timestamp,
        "date": date_stamp,
        "phase": current_phase,
        "session_summary": session_summary,
        "known_issues": known_issues,
        "active_tasks": len([t for t in active_tasks if t.get("status") != "completed"]),
        "completed_tasks": len(completed_tasks),
    }
    log.append(log_entry)
    _save_handoff_log(path, log)

    ctx_md = root / ".project-context.md"
    ctx_md.write_text(handoff_md, encoding="utf-8")

    return f"Handoff saved to {md_file}\n\nPreview:\n\n{handoff_md[:1500]}"


@mcp.tool(
    name="get_last_handoff",
    description="Retrieve the most recent AI handoff document so a new AI session has full context.",
)
def get_last_handoff(path: str = ".") -> str:
    """Load the most recently saved handoff.

    The next AI agent calls this first to instantly understand the project state.

    Args:
        path: Project root directory.
    """
    handoffs_dir = _handoffs_path(path)

    log = _load_handoff_log(path)
    if log:
        latest = log[-1]
        md_file = handoffs_dir / f"{latest.get('date', '')}.md"
        if md_file.exists():
            return md_file.read_text(encoding="utf-8")

    md_files = sorted(handoffs_dir.glob("*.md"), reverse=True)
    if md_files:
        return md_files[0].read_text(encoding="utf-8")

    root = validate_path(path)
    ctx_md = root / ".project-context.md"
    if ctx_md.exists():
        return ctx_md.read_text(encoding="utf-8")

    return (
        "No handoff found. The project may be new or no sessions have been recorded.\n\n"
        "Suggested next steps:\n"
        "1. `scan_project` — detect project structure\n"
        "2. `init_context` — set up project context\n"
        "3. `set_phase` — define the current development phase\n"
        "4. `create_task` — start tracking work"
    )


@mcp.tool(
    name="list_handoffs",
    description="List all AI session handoffs with dates.",
)
def list_handoffs(path: str = ".") -> str:
    """Show history of all handoff sessions.

    Args:
        path: Project root directory.
    """
    log = _load_handoff_log(path)
    if not log:
        return "No handoffs recorded yet. Use generate_handoff after your session."

    lines = ["# AI Handoff History\n"]
    for entry in reversed(log):
        lines.append(f"- **{entry.get('date', '?')}** — {entry.get('session_summary', 'No summary')[:80]}")
        lines.append(f"  Phase: {entry.get('phase', 'N/A')} | "
                      f"Active: {entry.get('active_tasks', 0)} | "
                      f"Completed: {entry.get('completed_tasks', 0)}")
    return "\n".join(lines)
