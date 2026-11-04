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


_CONFIG_CACHE: tuple[Path, float, str] | None = None


def get_project_root_and_safety() -> tuple[Path, str]:
    """
    Lazy-resolves the current active project root and reads its safety mode.
    
    Tries to read the active project root from the global app state.
    Falls back to current working directory.
    Uses mtime caching to avoid repeated disk reads on every file operation.
    """
    global _CONFIG_CACHE
    import app
    ctx = app._project_context
    if ctx is not None:
        root = ctx._root
    else:
        root = Path.cwd().resolve()
        
    config_file = root / ".project_brain" / "config.yaml"
    if config_file.is_file():
        try:
            mtime = config_file.stat().st_mtime
            if _CONFIG_CACHE is not None and _CONFIG_CACHE[0] == root and _CONFIG_CACHE[1] == mtime:
                return root, _CONFIG_CACHE[2]

            safety_mode = "safe"
            for line in config_file.read_text(encoding="utf-8").splitlines():
                line = line.split("#")[0].strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k.strip() == "safety_mode":
                        safety_mode = v.strip().lower()
            _CONFIG_CACHE = (root, mtime, safety_mode)
            return root, safety_mode
        except Exception:
            pass

    return root, "safe"


def validate_path(path: str | Path) -> Path:
    """
    Resolve a user-supplied path and ensure it is inside the project root
    (when safety_mode is 'safe' or 'trusted') or inside the allowed base
    directories list (when in 'lab' mode).
    Raises PermissionError if the path violates security constraints.
    """
    resolved = Path(path).resolve()
    root, safety_mode = get_project_root_and_safety()

    # Fast-path: If the path is already inside the project root (99.9% of operations)
    try:
        resolved.relative_to(root)
        return resolved
    except ValueError:
        if resolved == root:
            return resolved

    # Slow-path: Path is outside root. Check if we are in onboarding, switching or bootstrapping phase
    if safety_mode in ("safe", "trusted"):
        import inspect
        is_bootstrap = False
        for frame in inspect.stack():
            if frame.function in (
                "bootstrap_project",
                "create_project_workspace",
                "adopt_existing_project",
                "init_context",
                "load_context",
                "detect_and_init_context",
            ):
                is_bootstrap = True
                break

        if not is_bootstrap:
            raise PermissionError(
                f"Workspace Lock Active: Access to '{resolved}' is blocked. "
                f"Active safety mode '{safety_mode}' restricts all file operations to the project root '{root}'."
            )
        return resolved

    # Fallback for 'lab' mode: allowlist-based validation
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
