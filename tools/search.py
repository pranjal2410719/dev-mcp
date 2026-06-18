"""
Code search tool for dev-mcp.

Provides: search_code — ripgrep-based with Python fallback.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from app import mcp
from security import validate_path


@mcp.tool(description="Search for a text pattern across files in the project using ripgrep-like search.")
def search_code(
    pattern: str,
    path: str = ".",
    glob_filter: str | None = None,
    max_results: int = 50,
) -> str:
    """Search for *pattern* in source files. Uses ripgrep if available, otherwise a pure-Python fallback.

    Args:
        pattern: The text or regex pattern to search for.
        path: Directory to search in.
        glob_filter: Optional file pattern filter (e.g. '*.py', '*.ts', '*.{ts,js}').
        max_results: Maximum number of result lines to return.
    """
    base = validate_path(path)

    # Try ripgrep first (much faster)
    rg = shutil.which("rg")
    if rg:
        cmd = [rg, "--line-number", "--with-filename", "--color", "never", pattern]
        if glob_filter:
            cmd.extend(["--glob", glob_filter])
        cmd.extend([str(base)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if not output:
                return f"No matches found for '{pattern}' in {base}"
            lines = output.strip().split("\n")
            if len(lines) > max_results:
                lines = lines[:max_results]
                lines.append(f"... and {len(output.strip().split('\n')) - max_results} more results")
            return "\n".join(lines)
        except subprocess.TimeoutExpired:
            return f"Search timed out for '{pattern}'"

    # Pure-Python fallback
    import fnmatch as fnmatch_mod
    matches: list[str] = []
    compiled = re.compile(pattern)
    for root, _dirs, files in os.walk(base):
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
