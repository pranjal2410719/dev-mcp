"""
Orchestration and workflow management tools for Project Brain.

Provides: generate_project_brain, next_best_action, start_session, end_session
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from app import mcp, load_context as get_context
from security import validate_path
from brain.todo_engine import _load_todos, _load_completed
from brain.phase_manager import _load_milestones
from brain.handoff_engine import generate_handoff, get_last_handoff


def _is_git_repo(root: Path) -> bool:
    """Robust check to see if target directory is inside a Git repository."""
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.returncode == 0 and "true" in res.stdout.lower()
    except Exception:
        return False


def _get_recommendation(todos: list[dict], completed_ids: set[str], current_phase: str) -> dict[str, Any] | None:
    """Analyze dependencies and priorities to find the next logical task."""
    candidates = []
    for t in todos:
        if t.get("status") in ("completed", "cancelled"):
            continue
        if current_phase and t.get("phase") and t["phase"] != current_phase:
            continue
        deps = t.get("depends_on", [])
        if all(d in completed_ids for d in deps):
            candidates.append(t)
            
    if not candidates and current_phase:
        # Fallback to any phase if current phase has no active ready tasks
        for t in todos:
            if t.get("status") in ("completed", "cancelled"):
                continue
            deps = t.get("depends_on", [])
            if all(d in completed_ids for d in deps):
                candidates.append(t)
                
    if not candidates:
        return None
        
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    candidates.sort(key=lambda x: (priority_order.get(x.get("priority", "medium").lower(), 2), x.get("id", "")))
    
    best = candidates[0]
    
    # Estimate time & files
    priority = best.get("priority", "medium").lower()
    est = "1-2 hours" if priority == "critical" else "2-4 hours" if priority == "high" else "4-8 hours" if priority == "medium" else "8-16 hours"
    
    # Extract files to modify from description/title
    files = []
    text_to_search = f"{best.get('title', '')} {best.get('description', '')}"
    file_matches = re.findall(r'\b[\w\-\./]+\.(?:py|js|ts|tsx|jsx|json|html|css|toml|md|yml|yaml)\b', text_to_search)
    if file_matches:
        files = list(set(file_matches))
        
    return {
        "id": best.get("id", ""),
        "title": best.get("title", ""),
        "priority": best.get("priority", "medium"),
        "reason": "Highest priority unblocked task in current scope.",
        "files_affected": files if files else ["To be determined during planning"],
        "estimated_time": est
    }


@mcp.tool(
    name="generate_project_brain",
    description="Generate a complete aggregated Project Brain dashboard showing current status, phase, active/blocked tasks, recent changes, and recommendations.",
)
def generate_project_brain(path: str = ".") -> str:
    """Gather all project tracking details and produce a consolidated dashboard JSON."""
    root = validate_path(path)
    ctx = get_context(root)
    
    project_name = ctx.get("project.name", root.name)
    project_desc = ctx.get("project.description", "No description set")
    current_phase = ctx.get("project.current_phase", "Not set")
    
    # Load tasks
    todos = _load_todos(root)
    completed = _load_completed(root)
    
    # Milestones
    milestones = _load_milestones(root)
    active_milestone = "None"
    for m in milestones:
        if m.get("status") in ("active", "in_progress", "pending"):
            active_milestone = m.get("name", "Unnamed")
            break
            
    # Calculate progress %
    # Total tasks in current phase (if set)
    phase_todos = [t for t in todos if t.get("phase") == current_phase]
    phase_completed = [t for t in completed if t.get("phase") == current_phase]
    
    total_in_phase = len(phase_todos) + len(phase_completed)
    if total_in_phase > 0:
        progress_val = int((len(phase_completed) / total_in_phase) * 100)
        progress_str = f"{progress_val}% of current phase ({current_phase})"
    else:
        # Fallback to overall
        total_overall = len(todos) + len(completed)
        if total_overall > 0:
            progress_val = int((len(completed) / total_overall) * 100)
            progress_str = f"{progress_val}% overall"
        else:
            progress_str = "0% (no tasks)"
            
    # Active & Blocked tasks lists
    completed_ids = {t.get("id", "") for t in completed}
    blocked_tasks = []
    active_tasks = []
    
    for t in todos:
        status = t.get("status", "pending")
        t_id = t.get("id", "")
        t_title = t.get("title", "")
        
        # Check if blocked by dependencies
        deps = t.get("depends_on", [])
        unmet_deps = [d for d in deps if d not in completed_ids]
        
        if status == "blocked" or unmet_deps:
            reason = "Blocked by status" if status == "blocked" else f"Waiting on: {', '.join(unmet_deps)}"
            blocked_tasks.append({"id": t_id, "title": t_title, "reason": reason})
        elif status in ("in_progress", "pending"):
            active_tasks.append({"id": t_id, "title": t_title, "priority": t.get("priority", "medium")})
            
    # Recent changes (git commits)
    recent_changes = []
    if _is_git_repo(root):
        try:
            res = subprocess.run(
                ["git", "-C", str(root), "log", "-3", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout:
                recent_changes = [line.strip() for line in res.stdout.strip().split("\n")]
        except Exception:
            pass
            
    if not recent_changes:
        recent_changes = ["No recent changes recorded"]

    # Recommendation
    recommendation = _get_recommendation(todos, completed_ids, current_phase)
    
    dashboard = {
        "project": project_name,
        "description": project_desc,
        "current_phase": current_phase,
        "current_milestone": active_milestone,
        "progress": progress_str,
        "blocked_tasks": blocked_tasks,
        "active_tasks": active_tasks,
        "recent_changes": recent_changes,
        "next_recommended_task": recommendation
    }
    
    return json.dumps(dashboard, indent=2)


@mcp.tool(
    name="next_best_action",
    description="Intelligently calculate and recommend the next best task to work on based on phase, priority, dependencies, and file hints.",
)
def next_best_action(path: str = ".") -> str:
    """Suggest the next logical development task with files and reasons."""
    root = validate_path(path)
    todos = _load_todos(root)
    completed = _load_completed(root)
    completed_ids = {t.get("id", "") for t in completed}
    ctx = get_context(root)
    current_phase = ctx.get("project.current_phase", "")
    
    rec = _get_recommendation(todos, completed_ids, current_phase)
    if not rec:
        return "No ready tasks found in your project. Add tasks using create_task."
        
    files_str = "\n".join(f"- {f}" for f in rec["files_affected"])
    return (
        f"### Recommended Next Task: {rec['id']}\n\n"
        f"**Title:** {rec['title']}\n"
        f"**Priority:** {rec['priority'].upper()}\n"
        f"**Estimated Time:** {rec['estimated_time']}\n\n"
        f"**Reason:**\n{rec['reason']}\n\n"
        f"**Suggested Files:**\n{files_str}"
    )


@mcp.tool(
    name="start_session",
    description="Start a development session. Loads state, PRD, active tasks, and latest handoff to generate a detailed Session Brief for the AI.",
)
def start_session(path: str = ".") -> str:
    """Prepare and output a markdown starting session brief."""
    root = validate_path(path)
    ctx = get_context(root)
    
    project_name = ctx.get("project.name", root.name)
    current_phase = ctx.get("project.current_phase", "Not set")
    
    # Load PRD info
    prd_path = root / ".project_brain" / "prd" / "PRD.md"
    prd_excerpt = ""
    if prd_path.exists():
        prd_excerpt = prd_path.read_text(encoding="utf-8")[:500] + "..."
    else:
        prd_excerpt = "No PRD.md loaded yet."
        
    # Get last handoff
    last_handoff = get_last_handoff(str(root))
    
    # Get recommended task
    todos = _load_todos(root)
    completed = _load_completed(root)
    completed_ids = {t.get("id", "") for t in completed}
    rec = _get_recommendation(todos, completed_ids, current_phase)
    
    rec_str = "None (create tasks first)"
    if rec:
        rec_str = f"**{rec['id']}** — {rec['title']} (Priority: {rec['priority'].upper()}, Est: {rec['estimated_time']})"
        
    brief = [
        f"# 🚀 Dev Session Started — {project_name}",
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Current Phase:** {current_phase}",
        "",
        "## 🎯 Current Target Task",
        rec_str,
        "",
        "## 🤝 Last Session Handoff Summary",
        last_handoff[:1000] if len(last_handoff) > 1000 else last_handoff,
        "",
        "## 📝 PRD Brief",
        prd_excerpt,
        "",
        "## 🛠️ Next Steps for AI",
        "1. Focus strictly on the target task if ready, or review the blocked tasks.",
        "2. Keep the architecture rules in mind (run `validate_architecture` if unsure).",
        "3. When finished, summarize changes and call `end_session` to automatically commit and hand off."
    ]
    
    return "\n".join(brief)


@mcp.tool(
    name="end_session",
    description="End the current session, update progress, and generate a handoff file (does not auto-commit changes).",
)
def end_session(session_summary: str, known_issues: str = "", path: str = ".") -> str:
    """End development session, save status, and suggest git commit command."""
    root = validate_path(path)
    
    # Generate the handoff using existing engine
    handoff_res = generate_handoff(session_summary, known_issues, str(root))
    
    commit_suggestion = (
        "\n\n⚙️ **Handoff Complete.** Next, please review your changes by running:\n"
        "1. `prepare_commit` — to generate a suggested conventional commit message and review modified files.\n"
        "2. `commit_changes` — to apply the commit once approved."
    )
            
    return f"Session ended successfully!\n\n{handoff_res}{commit_suggestion}"


@mcp.tool(
    name="prepare_commit",
    description="Analyze modified workspace files and generate a suggested conventional git commit message and summary for approval.",
)
def prepare_commit(session_summary: str, path: str = ".") -> str:
    """Analyze workspace files and suggest a git commit message."""
    root = validate_path(path)
    
    modified_files = []
    untracked_files = []
    
    if _is_git_repo(root):
        try:
            status_res = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if status_res.returncode == 0:
                for line in status_res.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    state = line[:2].strip()
                    filepath = line[3:].strip()
                    if state in ("M", "AM", "MM"):
                        modified_files.append(filepath)
                    elif state in ("??", "A"):
                        untracked_files.append(filepath)
        except Exception:
            pass

    if not modified_files and not untracked_files:
        return "No modified or untracked files detected in workspace. Nothing to commit."

    # Determine conventional prefix based on files changed or summary
    prefix = "chore"
    summary_lower = session_summary.lower()
    
    # Analyze files to guess prefix
    all_changed = modified_files + untracked_files
    if any(f.endswith(".test.ts") or f.endswith(".test.js") or f.endswith("test_") or "test" in f for f in all_changed):
        prefix = "test"
    elif any("docs" in f or f.endswith(".md") for f in all_changed):
        prefix = "docs"
    elif any("refactor" in f or "clean" in f for f in all_changed):
        prefix = "refactor"
    elif any(f.endswith(".json") or f.endswith(".toml") or "config" in f for f in all_changed):
        prefix = "chore"
    
    # Refine prefix by description keyword
    if "fix" in summary_lower or "bug" in summary_lower or "resolve" in summary_lower:
        prefix = "fix"
    elif "add" in summary_lower or "create" in summary_lower or "feat" in summary_lower:
        prefix = "feat"
        
    # Guess scope (first modified folder or key file)
    scope = ""
    if all_changed:
        first_file = all_changed[0]
        parts = Path(first_file).parts
        if len(parts) > 1:
            scope = f"({parts[0]})"
            
    suggested_msg = f"{prefix}{scope}: {session_summary.strip()}"
    
    report = [
        "## 📝 Proposed Git Commit Details",
        "",
        f"**Suggested Commit Message:** `{suggested_msg}`",
        "",
        "### Changed Files for Review:",
        "- **Modified:**"
    ]
    for f in modified_files:
        report.append(f"  - `{f}`")
    report.append("- **Untracked / New:**")
    for f in untracked_files:
        report.append(f"  - `{f}`")
        
    report.extend([
        "",
        "👍 **To commit these changes, run:**",
        f'`commit_changes(message="{suggested_msg}")`'
    ])
    
    return "\n".join(report)


@mcp.tool(
    name="commit_changes",
    description="Stage all workspace changes and commit them to Git with the approved commit message.",
)
def commit_changes(message: str, path: str = ".") -> str:
    """Run git add . and git commit -m <message>."""
    root = validate_path(path)
    
    if not _is_git_repo(root):
        return "Not inside a valid Git repository."
        
    try:
        # 1. git add .
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        # 2. git commit -m message
        res = subprocess.run(
            ["git", "-C", str(root), "commit", "-m", message],
            capture_output=True,
            text=True
        )
        if res.returncode == 0:
            return f"✅ Changes committed successfully!\n\nCommit output:\n{res.stdout.strip()}"
        else:
            return f"❌ Commit failed:\n{res.stderr.strip() or res.stdout.strip()}"
    except Exception as e:
        return f"❌ Execution failed: {e}"

