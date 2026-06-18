"""
Reality Synchronization Engine for Project Brain.

Provides: sync_workspace, verify_work, project_dashboard
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from app import mcp, load_context as get_context
from security import validate_path
from brain.todo_engine import _load_todos, _load_completed
from brain.phase_manager import _load_milestones
from brain.handoff_engine import get_last_handoff
from brain.dependency import _get_graph
from brain.guardian import validate_architecture


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


@mcp.tool(
    name="sync_workspace",
    description="Scan the physical workspace (Git diff, new files, current branch, commits) and compare to the Todo plan to auto-detect finished work.",
)
def sync_workspace(path: str = ".") -> str:
    """Analyze files, git history, and code structure to synchronize active tasks with reality."""
    root = validate_path(path)
    
    # 1. Load active tasks
    todos = _load_todos(root)
    if not todos:
        return "No active tasks to synchronize. Create some tasks first."
        
    completed = _load_completed(root)
    completed_ids = {t.get("id", "") for t in completed}
    
    # 2. Check Git workspace details
    is_git = _is_git_repo(root)
    modified_files = []
    untracked_files = []
    deleted_files = []
    branch_name = ""
    recent_commit_msgs = []
    
    if is_git:
        try:
            # Get git status
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
                    elif state == "D":
                        deleted_files.append(filepath)
                        
            # Get branch name
            branch_res = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if branch_res.returncode == 0:
                branch_name = branch_res.stdout.strip()
                
            # Get last 5 commit logs
            log_res = subprocess.run(
                ["git", "-C", str(root), "log", "-5", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if log_res.returncode == 0:
                recent_commit_msgs = [l.strip() for l in log_res.stdout.splitlines()]
        except Exception:
            pass

    # 3. Compare Reality vs Plan for each task
    sync_results = []
    
    for t in todos:
        t_id = t.get("id", "")
        t_title = t.get("title", "")
        t_desc = t.get("description", "")
        t_status = t.get("status", "pending")
        
        if t_status == "completed":
            continue
            
        confidence = 0.0
        reasons = []
        
        # Heuristic A: Look for task ID or title keywords in branch name
        if branch_name and (t_id.lower() in branch_name.lower() or re.sub(r'[^a-zA-Z0-9]', '', t_id).lower() in branch_name.lower()):
            confidence += 0.60
            reasons.append(f"Current Git branch name matches task ID: `{branch_name}`")
        
        # Heuristic B: Look for task ID or title keywords in recent commits
        id_pattern = re.compile(rf"\b{re.escape(t_id)}\b", re.IGNORECASE)
        for commit in recent_commit_msgs:
            if id_pattern.search(commit):
                confidence += 0.50
                reasons.append(f"Task ID found in recent commit log: `{commit}`")
                break
                
        # Heuristic C: Look for files associated with task in modified/untracked list
        file_hints = re.findall(r'\b[\w\-\./]+\.(?:py|js|ts|tsx|jsx|json|html|css|toml)\b', f"{t_title} {t_desc}")
        matched_files = []
        for hint in file_hints:
            hint_name = Path(hint).name
            for f in modified_files + untracked_files:
                if Path(f).name == hint_name:
                    matched_files.append(f)
                    
        if matched_files:
            confidence += 0.40
            reasons.append(f"Associated task files were modified/added: {', '.join(matched_files)}")
            
        # Heuristic D: Simple keyword match in recently changed files
        title_keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', t_title)]
        keyword_file_match = False
        for kw in title_keywords:
            if kw in ("create", "add", "implement", "update", "delete", "remove", "task"):
                continue
            for f in modified_files + untracked_files:
                if kw in f.lower():
                    keyword_file_match = True
                    break
        if keyword_file_match:
            confidence += 0.20
            reasons.append("Task title keywords matched modified files.")
            
        confidence = min(confidence, 1.0)
        
        if confidence >= 0.60:
            sync_results.append({
                "id": t_id,
                "title": t_title,
                "confidence": confidence,
                "reasons": reasons,
                "recommendation": "mark_complete" if confidence >= 0.80 else "verify_work"
            })
            
    # Compile sync report
    report = [
        "# 🔄 Workspace Synchronization Report",
        f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 🛠️ Workspace Changes Detected (Git Reality)",
        f"- **Current Branch:** `{branch_name if branch_name else 'N/A'}`",
        f"- **Modified Files:** {len(modified_files)}",
        f"- **New Files:** {len(untracked_files)}",
        f"- **Deleted Files:** {len(deleted_files)}",
        ""
    ]
    
    if modified_files:
        report.append("### Modified Files:")
        for f in modified_files[:5]:
            report.append(f"- `{f}`")
        if len(modified_files) > 5:
            report.append(f"- ... and {len(modified_files) - 5} more")
        report.append("")
        
    if untracked_files:
        report.append("### New Files:")
        for f in untracked_files[:5]:
            report.append(f"- `{f}`")
        if len(untracked_files) > 5:
            report.append(f"- ... and {len(untracked_files) - 5} more")
        report.append("")
        
    report.append("## 📊 Reality vs. Todo Alignment")
    if sync_results:
        for res in sync_results:
            report.append(f"### 🎯 Task: **{res['id']}** — {res['title']}")
            report.append(f"- **Confidence:** {int(res['confidence'] * 100)}%")
            report.append("- **Evidence:**")
            for reason in res["reasons"]:
                report.append(f"  - {reason}")
            report.append(f"- **Recommended Action:** `{res['recommendation']}`")
            report.append("")
    else:
        report.append("All tasks align with plan. No autocompletion matches detected.")
        
    return "\n".join(report)


@mcp.tool(
    name="verify_work",
    description="Perform deep sanity, test, git diff, and architecture checks against a task to output a reality verification dossier.",
)
def verify_work(task_id: str, path: str = ".") -> str:
    """Verify code reality against a specific task definition and requirements."""
    root = validate_path(path)
    is_git = _is_git_repo(root)
    
    # Load task details
    todos = _load_todos(root)
    task = None
    for t in todos:
        if t.get("id") == task_id:
            task = t
            break
            
    if not task:
        completed = _load_completed(root)
        for t in completed:
            if t.get("id") == task_id:
                task = t
                break
                
    if not task:
        return f"Task {task_id} not found."
        
    t_title = task.get("title", "")
    t_desc = task.get("description", "")
    
    # 1. Parse target files from description or title
    file_hints = re.findall(r'\b[\w\-\./]+\.(?:py|js|ts|tsx|jsx|json|html|css|toml)\b', f"{t_title} {t_desc}")
    file_hints = list(set(file_hints))
    
    checklist = []
    confidence = 100
    
    if not file_hints:
        # Fallback keyword scan
        title_keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', t_title) if w.lower() not in ("create", "add", "implement", "update")]
        for kw in title_keywords:
            for dirpath, _, filenames in os.walk(root):
                for name in filenames:
                    if kw in name.lower() and Path(name).suffix in (".py", ".ts", ".tsx", ".js", ".jsx"):
                        file_hints.append(str((Path(dirpath) / name).relative_to(root)))
                        
    file_hints = list(set(file_hints))
    
    # 2. Check file existence
    files_found = []
    files_missing = []
    for f in file_hints:
        fp = Path(f)
        resolved_f = fp if fp.is_file() else root / fp
        if resolved_f.is_file():
            files_found.append(f)
        else:
            files_missing.append(f)
            
    if file_hints:
        if files_found:
            checklist.append(("✓ File Existence", f"Found {len(files_found)}/{len(file_hints)} expected files: {', '.join(files_found)}"))
        if files_missing:
            checklist.append(("✗ Missing Files", f"Expected files not found: {', '.join(files_missing)}"))
            confidence -= 30 * len(files_missing)
    else:
        checklist.append(("⚠️ Target Files", "Could not associate task to any file in the workspace."))
        confidence -= 40
        
    # 3. Check for test files
    has_tests = False
    test_files = []
    for f in files_found:
        f_name = Path(f).stem
        test_patterns = [f"test_{f_name}.py", f"{f_name}.test.ts", f"{f_name}.test.js", f"{f_name}.spec.ts"]
        for tp in test_patterns:
            for root_dir, _, files in os.walk(root):
                if tp in files:
                    test_files.append(str((Path(root_dir) / tp).relative_to(root)))
                    has_tests = True
                    
    if has_tests:
        checklist.append(("✓ Test Coverage", f"Found corresponding test files: {', '.join(test_files)}"))
    else:
        checklist.append(("⚠️ Test Coverage", "No dedicated test file matches found for target modules."))
        confidence -= 15
        
    # 4. Check for architecture violations in the created/modified files
    arch_report = validate_architecture(str(root))
    violations_in_task_files = []
    for f in files_found:
        if f in arch_report:
            violations_in_task_files.append(f)
            
    if violations_in_task_files:
        checklist.append(("✗ Architecture Control", f"Violations detected in task files: {', '.join(violations_in_task_files)}"))
        confidence -= 25
    else:
        checklist.append(("✓ Architecture Control", "All implementation files align with architectural rules."))
        
    # 5. Extract Git Diff Summary for modified files (if any)
    git_diff_summary = ""
    if is_git and files_found:
        try:
            diff_res = subprocess.run(
                ["git", "-C", str(root), "diff", "--stat", "HEAD", "--"] + files_found,
                capture_output=True,
                text=True,
                timeout=5
            )
            if diff_res.returncode == 0 and diff_res.stdout:
                git_diff_summary = diff_res.stdout.strip()
        except Exception:
            pass
            
    confidence = max(0, min(confidence, 100))
    
    report = [
        f"# 🕵️ Verification Dossier for `{task_id}`",
        f"**Task:** {t_title}",
        f"**Description:** {t_desc if t_desc else 'No description provided'}",
        f"**Verification Confidence:** {confidence}%",
        f"**Verdict:** {'Mark Complete ✅' if confidence >= 80 else 'Requires Work 🛠️' if confidence >= 50 else 'Failed ❌'}",
        "",
        "## 📋 Verification Checklist"
    ]
    
    for title, desc in checklist:
        report.append(f"- **{title}** — {desc}")
        
    if git_diff_summary:
        report.extend([
            "",
            "## 📁 Git Diff Stats for Task Files",
            "```text",
            git_diff_summary,
            "```"
        ])
        
    report.extend([
        "",
        "---",
        "### 🤖 AI Client Verification Instruction",
        "Analyze the checklist and Git diff summary above. Compare the implementation with the task description.",
        f"If you are reviewing this as the AI assistant, ensure the code changes fully resolve `{task_id}`.",
        "If there are missing criteria (e.g. error handling, validations, missing files), report them to the user."
    ])
    
    return "\n".join(report)


@mcp.tool(
    name="project_dashboard",
    description="Generate a unified Project Manager Dashboard combining phase state, todo progress, git status, architecture violations, and a project health score.",
)
def project_dashboard(path: str = ".") -> str:
    """Consolidated project status and metrics dashboard."""
    root = validate_path(path)
    ctx = get_context(root)
    is_git = _is_git_repo(root)
    
    project_name = ctx.get("project.name", root.name)
    current_phase = ctx.get("project.current_phase", "Not set")
    
    # Load tasks
    todos = _load_todos(root)
    completed = _load_completed(root)
    completed_ids = {t.get("id", "") for t in completed}
    
    # Phase details & Milestones
    milestones = _load_milestones(root)
    active_milestone = "None"
    for m in milestones:
        if m.get("status") in ("active", "in_progress", "pending"):
            active_milestone = m.get("name", "Unnamed")
            break
            
    # Calculate progress %
    phase_todos = [t for t in todos if t.get("phase") == current_phase]
    phase_completed = [t for t in completed if t.get("phase") == current_phase]
    total_in_phase = len(phase_todos) + len(phase_completed)
    
    if total_in_phase > 0:
        progress_val = int((len(phase_completed) / total_in_phase) * 100)
    else:
        total_overall = len(todos) + len(completed)
        progress_val = int((len(completed) / total_overall) * 100) if total_overall > 0 else 0

    # Task breakdowns
    blocked_tasks = []
    active_tasks = []
    stale_tasks_count = 0
    
    for t in todos:
        t_id = t.get("id", "")
        t_title = t.get("title", "")
        t_status = t.get("status", "pending")
        deps = t.get("depends_on", [])
        unmet_deps = [d for d in deps if d not in completed_ids]
        
        # Check staleness (older than 7 days)
        created_str = t.get("created", "")
        if created_str:
            try:
                created_dt = datetime.fromisoformat(created_str.split(".")[0])
                age = datetime.now() - created_dt
                if age.days > 7 and t_status in ("pending", "in_progress"):
                    stale_tasks_count += 1
            except Exception:
                pass

        if t_status == "blocked" or unmet_deps:
            reason = "Blocked status" if t_status == "blocked" else f"Waiting on: {', '.join(unmet_deps)}"
            blocked_tasks.append(f"{t_id} — {t_title} ({reason})")
        elif t_status in ("in_progress", "pending"):
            active_tasks.append(f"{t_id} — {t_title} [{t.get('priority', 'medium').upper()}]")

    # Git details
    modified_count = 0
    recent_changes = []
    if is_git:
        try:
            status_res = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if status_res.returncode == 0:
                modified_count = len(status_res.stdout.splitlines())
                
            log_res = subprocess.run(
                ["git", "-C", str(root), "log", "-3", "--oneline"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if log_res.returncode == 0:
                recent_changes = [l.strip() for l in log_res.stdout.splitlines()]
        except Exception:
            pass

    # Architecture Violations count
    arch_report = validate_architecture(str(root))
    violations_count = len(re.findall(r'- \*\*.*?\*\* \(Line \d+\): Found', arch_report))

    # Dependency risks (modified files that have high dependents counts)
    dependency_risks = []
    if is_git and modified_count > 0:
        try:
            _, dependents = _get_graph(root)
            for f_rel in dependents:
                is_modified = False
                status_res = subprocess.run(
                    ["git", "-C", str(root), "status", "--porcelain", f_rel],
                    capture_output=True,
                    text=True
                )
                if status_res.returncode == 0 and status_res.stdout.strip():
                    is_modified = True
                if is_modified:
                    deps_count = len(dependents[f_rel])
                    if deps_count > 2:
                        dependency_risks.append(f"`{f_rel}` (used by {deps_count} files)")
        except Exception:
            pass

    # Calculate Health Score
    health_score = 100
    health_score -= len(blocked_tasks) * 5
    health_score -= violations_count * 15
    health_score -= stale_tasks_count * 3
    health_score -= len(dependency_risks) * 5
    health_score = max(0, min(health_score, 100))

    # Next Task recommendation
    from brain.orchestrator import _get_recommendation
    rec = _get_recommendation(todos, completed_ids, current_phase)
    next_task_str = "None (Use `create_task` to add tasks)"
    if rec:
        next_task_str = f"**{rec['id']}** — {rec['title']} (Est: {rec['estimated_time']})"

    last_handoff = get_last_handoff(str(root))
    last_handoff_summary = "None"
    for line in last_handoff.splitlines():
        if line.startswith("**Session Date:**") or line.startswith("## Session Summary"):
            last_handoff_summary = line.strip()
            
    dashboard = [
        f"# 📊 Project Manager Dashboard: `{project_name}`",
        f"**Phase:** {current_phase} | **Milestone:** {active_milestone}",
        f"**Plan Progress:** {progress_val}% | **Health Score:** {health_score}/100",
        "",
        "## 🎯 Current Focus",
        f"- **Next Task:** {next_task_str}",
        "",
        "## 📋 Task Diagnostics",
        f"- **Active Tasks:** {len(active_tasks)}",
        f"- **Blocked Tasks:** {len(blocked_tasks)}",
        f"- **Stale Tasks (Old):** {stale_tasks_count}",
        ""
    ]

    if blocked_tasks:
        dashboard.append("### Blocked Tasks Detail:")
        for bt in blocked_tasks[:3]:
            dashboard.append(f"  - {bt}")
        dashboard.append("")

    dashboard.extend([
        "## 🛡️ Architecture & Dependency Diagnostics",
        f"- **Architecture Violations:** {violations_count}",
        f"- **Blast Radius Risks:** {len(dependency_risks)}"
    ])

    if dependency_risks:
        dashboard.append("### High Risk Edited Files:")
        for dr in dependency_risks:
            dashboard.append(f"  - {dr}")
        dashboard.append("")

    dashboard.extend([
        "",
        "## 📂 Git Workspace Reality",
        f"- **Uncommitted Modified Files:** {modified_count}",
        "- **Recent Commits:**"
    ])
    for commit in recent_changes:
        dashboard.append(f"  - `{commit}`")

    dashboard.extend([
        "",
        "## 🤝 Handoff Context",
        f"- **Last Session Activity:** {last_handoff_summary}"
    ])

    return "\n".join(dashboard)
