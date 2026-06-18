"""
Todo Engine for Project Brain.

Structured task management with phase association, priorities,
dependencies, and status tracking.  Replaces the simple
'active_tasks' list with a full task engine.

Data stored in .project_brain/todos/
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

VALID_STATUSES = {"pending", "in_progress", "blocked", "completed", "cancelled"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}

TASKS_FILE = "active.json"
COMPLETED_FILE = "completed.json"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _todos_path(project_root: str | Path) -> Path:
    r = validate_path(project_root)
    p = r / ".project_brain" / "todos"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_todos(root: str | Path) -> list[dict]:
    p = _todos_path(root) / TASKS_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def _save_todos(root: str | Path, todos: list[dict]) -> None:
    p = _todos_path(root) / TASKS_FILE
    p.write_text(json.dumps(todos, indent=2), encoding="utf-8")


def _load_completed(root: str | Path) -> list[dict]:
    p = _todos_path(root) / COMPLETED_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return []


def _save_completed(root: str | Path, todos: list[dict]) -> None:
    p = _todos_path(root) / COMPLETED_FILE
    p.write_text(json.dumps(todos, indent=2), encoding="utf-8")


def _next_task_id(todos: list[dict]) -> str:
    existing_ids = {t.get("id", "") for t in todos}
    n = 1
    while f"TASK-{n:04d}" in existing_ids:
        n += 1
    return f"TASK-{n:04d}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(
    name="create_task",
    description="Create a new task with phase, priority, dependencies, and description.",
)
def create_task(
    title: str,
    phase: str = "",
    priority: str = "medium",
    depends_on: str = "",
    description: str = "",
    path: str = ".",
) -> str:
    """Add a structured task to the todo engine.

    Args:
        title: Short task title.
        phase: Which phase this task belongs to (leave empty for current phase).
        priority: One of: critical, high, medium, low.
        depends_on: Comma-separated task IDs that must be completed first.
        description: Longer description / acceptance criteria.
        path: Project root directory.
    """
    todos = _load_todos(path)
    task_id = _next_task_id(todos)
    ctx = get_context(path)

    if not phase:
        phase = ctx.get("project.current_phase", "")

    priority = priority.lower()
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    deps = [d.strip() for d in depends_on.split(",") if d.strip()] if depends_on else []

    task = {
        "id": task_id,
        "title": title,
        "phase": phase,
        "priority": priority,
        "status": "pending",
        "depends_on": deps,
        "description": description,
        "created": datetime.now().isoformat(),
    }
    todos.append(task)
    _save_todos(path, todos)

    ctx.append("active_tasks", {
        "id": task_id,
        "description": title,
        "status": "pending",
        "phase": phase,
        "priority": priority,
    })

    return f"Created {task_id}: {title} [{priority}]"


@mcp.tool(
    name="update_task",
    description="Update a task's status, priority, or description by ID.",
)
def update_task(
    task_id: str,
    status: str = "",
    priority: str = "",
    title: str = "",
    path: str = ".",
) -> str:
    """Modify an existing task.

    Args:
        task_id: The task ID (e.g. TASK-0001).
        status: One of: pending, in_progress, blocked, completed, cancelled.
        priority: One of: critical, high, medium, low.
        title: New title (if changing).
        path: Project root directory.
    """
    todos = _load_todos(path)
    found = False
    changes = []

    for t in todos:
        if t.get("id") == task_id:
            found = True
            if status and status in VALID_STATUSES:
                t["status"] = status
                changes.append(f"status→{status}")
                if status == "completed":
                    t["completed"] = datetime.now().isoformat()
            if priority and priority in VALID_PRIORITIES:
                t["priority"] = priority
                changes.append(f"priority→{priority}")
            if title:
                t["title"] = title
                changes.append("title updated")
            break

    if not found:
        return f"Task {task_id} not found."

    _save_todos(path, todos)

    # If completed, move to completed.json (file-based, always works)
    if status == "completed":
        completed = _load_completed(path)
        # Find the task in the saved todos to move it
        for t in todos:
            if t.get("id") == task_id:
                completed.append(t)
                break
        _save_completed(path, completed)

    # Sync status to context (best-effort)
    if status:
        ctx = get_context(path)
        active = ctx.data.get("active_tasks", [])
        for i, t in enumerate(active):
            if isinstance(t, dict) and t.get("id") == task_id:
                if status == "completed":
                    ctx.remove_from("active_tasks", i)
                else:
                    ctx.set(f"active_tasks.{i}.status", status)
                break

    return f"Updated {task_id}: {', '.join(changes)}"


@mcp.tool(
    name="complete_task",
    description="Mark a task as completed with optional notes.",
)
def complete_task(task_id: str, notes: str = "", path: str = ".") -> str:
    """Mark a task done and move it to completed history.

    Args:
        task_id: The task ID to complete.
        notes: Completion notes.
        path: Project root directory.
    """
    return update_task(task_id=task_id, status="completed", path=path) + (
        f"\nNotes: {notes}" if notes else ""
    )


@mcp.tool(
    name="next_task",
    description="Get the highest-priority task that is ready to work on (dependencies met, current phase).",
)
def next_task(path: str = ".") -> str:
    """Find the most important task that can be started now.

    Only considers tasks in the current phase whose dependencies are met.

    Args:
        path: Project root directory.
    """
    todos = _load_todos(path)
    ctx = get_context(path)
    current_phase = ctx.get("project.current_phase", "")
    completed_ids = {t.get("id", "") for t in _load_completed(path)}

    candidates = []
    for t in todos:
        if t.get("status") in ("completed", "cancelled"):
            continue
        if current_phase and t.get("phase") and t["phase"] != current_phase:
            continue
        deps = t.get("depends_on", [])
        deps_met = all(d in completed_ids for d in deps)
        if not deps_met:
            continue
        candidates.append(t)

    if not candidates:
        if todos:
            return "No ready tasks in the current phase. Check blocked_tasks or create_task."
        return "No tasks defined. Use create_task to start."

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    candidates.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 2))

    best = candidates[0]
    deps_str = f" Depends on: {', '.join(best.get('depends_on', []))}" if best.get("depends_on") else ""
    return (
        f"## Next Task: {best['id']}\n\n"
        f"**Title:** {best.get('title', '')}\n"
        f"**Priority:** {best.get('priority', 'medium')}\n"
        f"**Phase:** {best.get('phase', 'N/A')}\n"
        f"**Status:** {best.get('status', 'pending')}{deps_str}\n"
        f"**Description:** {best.get('description', '')}\n"
    )


@mcp.tool(
    name="blocked_tasks",
    description="List all tasks that are blocked, either by dependencies or explicitly.",
)
def blocked_tasks(path: str = ".") -> str:
    """Show tasks that cannot proceed.

    Args:
        path: Project root directory.
    """
    todos = _load_todos(path)
    completed_ids = {t.get("id", "") for t in _load_completed(path)}
    blocked = []

    for t in todos:
        if t.get("status") == "blocked":
            blocked.append((t, "Explicitly blocked"))
        elif t.get("status") not in ("completed", "cancelled"):
            deps = t.get("depends_on", [])
            unmet = [d for d in deps if d not in completed_ids]
            if unmet:
                blocked.append((t, f"Waiting on: {', '.join(unmet)}"))

    if not blocked:
        return "No blocked tasks. 🎉"

    lines = ["# Blocked Tasks\n"]
    for t, reason in blocked:
        lines.append(f"- **{t.get('id', '?')}** — {t.get('title', '')}")
        lines.append(f"  Reason: {reason}")
    return "\n".join(lines)


@mcp.tool(
    name="list_tasks",
    description="List all active tasks, optionally filtered by phase or status.",
)
def list_tasks(
    phase: str = "",
    status: str = "",
    priority: str = "",
    path: str = ".",
) -> str:
    """Display tasks with optional filters.

    Args:
        phase: Filter by phase name.
        status: Filter by status (pending, in_progress, blocked, completed).
        priority: Filter by priority (critical, high, medium, low).
        path: Project root directory.
    """
    todos = _load_todos(path)
    completed = {t.get("id") for t in _load_completed(path)}

    if phase:
        todos = [t for t in todos if t.get("phase") == phase]
    if status:
        todos = [t for t in todos if t.get("status") == status]
    if priority:
        todos = [t for t in todos if t.get("priority") == priority]

    if not todos:
        return "No tasks matching the filters."

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    todos.sort(key=lambda t: (priority_order.get(t.get("priority", "medium"), 2), t.get("id", "")))

    lines = ["# Tasks\n"]
    for t in todos:
        icon = "✅" if t.get("id") in completed else "🔄" if t.get("status") == "in_progress" else "🔴" if t.get("status") == "blocked" else "📋"
        lines.append(f"{icon} **{t.get('id', '?')}** — {t.get('title', '')}")
        lines.append(f"   [{t.get('priority', 'medium')}] phase: {t.get('phase', 'N/A')} status: {t.get('status', 'pending')}")
        deps = t.get("depends_on", [])
        if deps:
            lines.append(f"   depends on: {', '.join(deps)}")

    total = len(todos)
    done_count = sum(1 for t in todos if t.get("status") == "completed" or t.get("id") in completed)
    lines.append(f"\n---\n{total} tasks ({done_count} completed)")

    return "\n".join(lines)
