"""
Security helpers for dev-mcp.

Provides path validation to ensure all file operations stay within
allowed directories.
"""

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Allowed directories (lazy-initialized)
# ---------------------------------------------------------------------------

_ALLOWED_DIRS: list[Path] = []


def get_allowed_dirs() -> list[Path]:
    """Return the list of allowed base directories, computing it once."""
    global _ALLOWED_DIRS
    if not _ALLOWED_DIRS:
        # Always allow CWD
        _ALLOWED_DIRS.append(Path.cwd().resolve())

        # Allow paths from environment variable
        env_dirs = os.environ.get("DEV_MCP_ALLOWED_DIRS", "")
        if env_dirs:
            for d in env_dirs.split(":"):
                p = Path(d).resolve()
                if p.exists():
                    _ALLOWED_DIRS.append(p)

        # Also allow HOME by default
        home = Path.home()
        if home not in _ALLOWED_DIRS:
            _ALLOWED_DIRS.append(home)

    return _ALLOWED_DIRS


def validate_path(path: str | Path) -> Path:
    """
    Resolve a user-supplied path and ensure it is inside one of the allowed
    base directories.  Raises PermissionError if the path is outside.
    """
    resolved = Path(path).resolve()
    allowed = get_allowed_dirs()
    for base in allowed:
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    raise PermissionError(
        f"Access denied: '{resolved}' is not in any allowed directory "
        f"({', '.join(str(d) for d in allowed)})"
    )
