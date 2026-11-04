"""
Code search tool for dev-mcp.

Provides: search_code — high-speed ripgrep-based search with automatic noise exclusion
and pure-Python fallback.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from app import mcp
from security import validate_path


EXCLUDE_GLOBS = [
    "!.git/*",
    "!.venv/*",
    "!venv/*",
    "!node_modules/*",
    "!__pycache__/*",
    "!.pytest_cache/*",
    "!dist/*",
    "!build/*",
    "!.project_brain_archive/*",
]


@mcp.tool(
    name="search_code",
    description="Search for a text or regex pattern across codebase with ripgrep, noise exclusion, and context lines.",
)
def search_code(
    pattern: str,
    path: str = ".",
    glob_filter: str | None = None,
    max_results: int = 50,
    context_lines: int = 0,
    case_sensitive: bool = False,
) -> str:
    """Search for *pattern* in source files using ripgrep with smart noise filtering.

    Args:
        pattern: The text or regex pattern to search for.
        path: Directory to search in (default: current directory).
        glob_filter: Optional file pattern filter (e.g. '*.py', '*.ts', '*.{ts,js}').
        max_results: Maximum number of result lines to return.
        context_lines: Number of surrounding context lines to show (0 = match line only).
        case_sensitive: If True, enforces strict case sensitivity.
    """
    base = validate_path(path)

    # Fast-path: Ripgrep
    rg = shutil.which("rg")
    if rg:
        cmd = [rg, "--line-number", "--with-filename", "--color", "never"]

        if case_sensitive:
            cmd.append("--case-sensitive")
        else:
            cmd.append("--smart-case")

        if context_lines > 0:
            cmd.extend(["-C", str(min(context_lines, 5))])

        # Exclude noisy build and cache folders
        for exc in EXCLUDE_GLOBS:
            cmd.extend(["--glob", exc])

        if glob_filter:
            cmd.extend(["--glob", glob_filter])

        cmd.extend([pattern, str(base)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if not output:
                return f"No matches found for '{pattern}' in {base}"

            lines = output.strip().splitlines()
            total_matches = len(lines)
            if total_matches > max_results:
                lines = lines[:max_results]
                lines.append(f"... and {total_matches - max_results} more matching lines.")
            return "\n".join(lines)
        except subprocess.TimeoutExpired:
            return f"Search timed out after 30 seconds for '{pattern}'"

    # Pure-Python fallback (skipping noise directories)
    import fnmatch as fnmatch_mod
    matches: list[str] = []
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)

    for root, dirs, files in os.walk(base):
        # Prune noisy directories in-place
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "node_modules", "__pycache__", "dist"}]

        for fname in files:
            if glob_filter and not fnmatch_mod.fnmatch(fname, glob_filter):
                continue
            fpath = Path(root) / fname
            try:
                for i, line in enumerate(fpath.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if compiled.search(line):
                        rel = fpath.relative_to(base)
                        matches.append(f"{rel}:{i}:{line}")
                        if len(matches) >= max_results:
                            break
            except Exception:
                continue
        if len(matches) >= max_results:
            break

    if not matches:
        return f"No matches found for '{pattern}' in {base}"
    return "\n".join(matches)
