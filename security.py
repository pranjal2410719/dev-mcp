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


def get_project_root_and_safety() -> tuple[Path, str]:
    """
    Lazy-resolves the current active project root and reads its safety mode.
    
    Tries to read the active project root from the global app state.
    Falls back to current working directory.
    Safety mode defaults to 'safe' unless overridden in config.yaml.
    """
    import app
    ctx = app._project_context
    if ctx is not None:
        root = ctx._root
    else:
        root = Path.cwd().resolve()
        
    safety_mode = "safe"  # default safety mode
    config_file = root / ".project_brain" / "config.yaml"
    if config_file.is_file():
        try:
            for line in config_file.read_text(encoding="utf-8").splitlines():
                line = line.split("#")[0].strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k.strip() == "safety_mode":
                        safety_mode = v.strip().lower()
        except Exception:
            pass
    return root, safety_mode


def validate_path(path: str | Path) -> Path:
    """
    Resolve a user-supplied path and ensure it is inside the project root
    (when safety_mode is 'safe' or 'trusted') or inside the allowed base
    directories list (when in 'lab' mode).
    Raises PermissionError if the path violates security constraints.
    """
    resolved = Path(path).resolve()
    
    root, safety_mode = get_project_root_and_safety()
    
    # Check if we are in onboarding or bootstrapping phase
    import inspect
    is_bootstrap = False
    for frame in inspect.stack():
        if frame.function in ("bootstrap_project", "create_project_workspace", "adopt_existing_project"):
            is_bootstrap = True
            break

    # If safety_mode is 'safe' or 'trusted', enforce Workspace Lock (path must be under root),
    # unless we are currently bootstrapping or adopting a new project.
    if safety_mode in ("safe", "trusted") and not is_bootstrap:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            if resolved == root:
                return resolved
            raise PermissionError(
                f"Workspace Lock Active: Access to '{resolved}' is blocked. "
                f"Active safety mode '{safety_mode}' restricts all file operations to the project root '{root}'."
            )
            
    # Else ('lab' mode or unconfigured), fallback to the original allowlist-based validation
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
