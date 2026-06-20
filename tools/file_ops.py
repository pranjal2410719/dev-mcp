"""
File operation tools for dev-mcp.

Provides: read_file, write_file, edit_file, delete_path, delete_recursive,
          list_directory, glob_files, create_directory
"""

from __future__ import annotations

import glob as glob_module
import shutil
from pathlib import Path

from app import mcp
from security import validate_path


@mcp.tool(description="Read the contents of a file at the given path.")
def read_file(path: str) -> str:
    """Read and return the full contents of a text file.

    Args:
        path: Relative or absolute path to the file.
    """
    p = validate_path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        size = p.stat().st_size
        return f"[Binary file – {size} bytes]"


@mcp.tool(description="Write content to a file, creating it if it doesn't exist.")
def write_file(path: str, content: str) -> str:
    """Write text content to a file.  Overwrites existing content.

    Args:
        path: Relative or absolute path to the file.
        content: The text content to write.
    """
    p = validate_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} characters to {p}"


@mcp.tool(
    description="Edit a file by replacing an exact string with a new string. "
    "Use this for targeted code changes instead of rewriting the whole file."
)
def edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace occurrences of *old_string* with *new_string* in a file.

    Args:
        path: Relative or absolute path to the file.
        old_string: The exact string to find (case-sensitive, whitespace-sensitive).
        new_string: The replacement string.
    """
    p = validate_path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    content = p.read_text(encoding="utf-8")
    if old_string not in content:
        raise ValueError(
            f"The specified old_string was not found in {p}.\n"
            f"Make sure you match whitespace and punctuation exactly."
        )

    count = content.count(old_string)
    new_content = content.replace(old_string, new_string)
    p.write_text(new_content, encoding="utf-8")
    return f"Replaced {count} occurrence(s) in {p}"


@mcp.tool(description="Delete a file or an empty directory.")
def delete_path(path: str) -> str:
    """Delete a file or empty directory.

    Args:
        path: Relative or absolute path to the file/directory.
    """
    p = validate_path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")
    if p.is_file():
        p.unlink()
        return f"Deleted file: {p}"
    if p.is_dir():
        try:
            p.rmdir()
            return f"Deleted empty directory: {p}"
        except OSError:
            raise ValueError(
                f"Directory is not empty: {p}. "
                "Use delete_recursive for non-empty directories."
            )
    return f"Unknown path type: {p}"


@mcp.tool(description="Recursively delete a file or directory tree. Use with caution.")
def delete_recursive(path: str) -> str:
    """Recursively delete a file or directory (like rm -rf).

    Args:
        path: Relative or absolute path to the file/directory.
    """
    p = validate_path(path)
    
    # Restrict destructive operations under safe mode
    from security import get_project_root_and_safety
    _, safety_mode = get_project_root_and_safety()
    if safety_mode == "safe":
        raise PermissionError(
            f"Action Blocked: 'delete_recursive' is forbidden under safety mode '{safety_mode}'. "
            "Please upgrade the 'safety_mode' to 'trusted' or 'lab' in your .project_brain/config.yaml configuration to run destructive operations."
        )

    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")
    shutil.rmtree(p)
    return f"Deleted recursively: {p}"


@mcp.tool(description="List files and directories inside a given directory.")
def list_directory(path: str) -> str:
    """List all entries in a directory.

    Args:
        path: Relative or absolute path to the directory.
    """
    p = validate_path(path)
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {p}")
    entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
    lines = []
    for entry in entries:
        suffix = "/" if entry.is_dir() else ""
        size = entry.stat().st_size if entry.is_file() else 0
        lines.append(f"{entry.name}{suffix}  ({size:,} bytes)" if entry.is_file() else f"{entry.name}{suffix}")
    return "\n".join(lines)


@mcp.tool(description="Find files matching a glob pattern (e.g. '**/*.ts', 'src/**/*.py').")
def glob_files(pattern: str, base_path: str = ".") -> str:
    """Search for files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g. '**/*.py', 'src/**/*.ts', '*.json').
        base_path: Directory to search from (default: current directory).
    """
    base = validate_path(base_path)
    matches = sorted(glob_module.glob(pattern, root_dir=base, recursive=True))
    if not matches:
        return f"No files matching '{pattern}' in {base}"
    return "\n".join(str(m) for m in matches)


@mcp.tool(description="Create one or more directories (like mkdir -p).")
def create_directory(path: str) -> str:
    """Create a directory, including any missing parents.

    Args:
        path: Relative or absolute path to the directory.
    """
    p = validate_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Created directory: {p}"
