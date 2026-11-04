"""
Git operation tools for dev-mcp.

Provides: git_status, git_diff, git_log, git_branch, git_add,
          git_commit, git_create_branch
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from app import mcp
from security import validate_path


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _git_cmd(repo_path: str | None, *args: str) -> str:
    """Run a git command and return its stdout."""
    cwd = str(validate_path(repo_path)) if repo_path else str(Path.cwd())
    try:
        result = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output_parts = []
        if result.stdout:
            output_parts.append(result.stdout.strip())
        if result.stderr:
            output_parts.append(f"--- stderr ---\n{result.stderr.strip()}")
        status = f"[Exit code: {result.returncode}]"
        return f"{status}\n{"\n".join(output_parts)}" if output_parts else status
    except FileNotFoundError:
        return "Git is not installed or not found in PATH."
    except subprocess.TimeoutExpired:
        return "[Git command timed out]"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(description="Show the working tree status (git status).")
def git_status(repo_path: str = ".") -> str:
    """Show the current git status of the repository.

    Args:
        repo_path: Path to the git repository.
    """
    return _git_cmd(repo_path, "status")


@mcp.tool(description="Show staged and unstaged changes (git diff).")
def git_diff(repo_path: str = ".", staged: bool = False) -> str:
    """Show file changes.

    Args:
        repo_path: Path to the git repository.
        staged: If True, show only staged changes (git diff --cached).
    """
    args = ["diff", "--cached"] if staged else ["diff"]
    return _git_cmd(repo_path, *args)


@mcp.tool(description="Show recent commit history (git log).")
def git_log(repo_path: str = ".", max_count: int = 10) -> str:
    """Display the commit log.

    Args:
        repo_path: Path to the git repository.
        max_count: Maximum number of commits to show.
    """
    return _git_cmd(repo_path, "log", f"--max-count={max_count}", "--oneline", "--graph")


@mcp.tool(description="List local branches (git branch).")
def git_branch(repo_path: str = ".") -> str:
    """List all local branches.

    Args:
        repo_path: Path to the git repository.
    """
    return _git_cmd(repo_path, "branch")


@mcp.tool(description="Stage file(s) for commit (git add).")
def git_add(repo_path: str = ".", files: str = ".") -> str:
    """Stage file changes.

    Args:
        repo_path: Path to the git repository.
        files: File(s) to stage (space-separated, or '.' for all).
    """
    return _git_cmd(repo_path, "add", *files.split())


@mcp.tool(description="Commit staged changes with a message (git commit).")
def git_commit(repo_path: str = ".", message: str = "update") -> str:
    """Create a new commit.

    Args:
        repo_path: Path to the git repository.
        message: Commit message.
    """
    return _git_cmd(repo_path, "commit", "-m", message)


@mcp.tool(description="Create and switch to a new git branch (git checkout -b).")
def git_create_branch(repo_path: str = ".", branch_name: str = "") -> str:
    """Create a new branch and switch to it.

    Args:
        repo_path: Path to the git repository.
        branch_name: Name for the new branch.
    """
    if not branch_name:
        return "Error: branch_name is required."
    return _git_cmd(repo_path, "checkout", "-b", branch_name)


@mcp.tool(
    name="install_git_hooks",
    description="Install automated pre-commit hook to sync Project Brain and context with native terminal git commits.",
)
def install_git_hooks(repo_path: str = ".", hook_type: str = "pre-commit") -> str:
    """Install automated Git hook in the target repository to auto-sync .project_brain and context.

    Args:
        repo_path: Path to the git repository (defaults to project root).
        hook_type: Hook to install ('pre-commit' or 'post-commit').
    """
    root = validate_path(repo_path)
    git_dir = root / ".git"
    if not git_dir.is_dir():
        return f"Error: No .git directory found at '{root}'. Please initialize git first."

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / hook_type

    hook_script = f"""#!/bin/sh
# dev-mcp automated {hook_type} hook
# Automatically syncs .project_brain and .project-context.json on git commits

REPO_DIR="$(git rev-parse --show-toplevel)"
cd "$REPO_DIR" || exit 1

# Check if Project Brain or Context exists
if [ -d ".project_brain" ] || [ -f ".project-context.json" ]; then
    # Auto-stage Project Brain and Context files if they changed
    git add .project_brain .project-context.json 2>/dev/null || true
fi

exit 0
"""
    try:
        hook_file.write_text(hook_script, encoding="utf-8")
        import os
        os.chmod(hook_file, 0o755)
        return f"✅ Successfully installed {hook_type} hook at: {hook_file.relative_to(root)}\nYour Project Brain will now stay synchronized with native terminal git commits."
    except Exception as e:
        return f"Failed to install git hook: {str(e)}"

