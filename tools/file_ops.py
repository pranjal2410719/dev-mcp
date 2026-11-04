"""
File operation tools for dev-mcp.

Provides: read_file, write_file, edit_file, batch_replace, delete_path,
          delete_recursive, list_directory, glob_files, create_directory, file_info
"""

from __future__ import annotations

import glob as glob_module
import os
import shutil
import tempfile
from pathlib import Path

from app import mcp
from security import validate_path


IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}


def _format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@mcp.tool(
    name="read_file",
    description="Read the contents of a file with optional line-range slicing and line numbering.",
)
def read_file(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    line_numbers: bool = False,
) -> str:
    """Read and return contents of a file. Supports line range slicing and line numbers.

    Args:
        path: Relative or absolute path to the file.
        start_line: 1-indexed start line (optional).
        end_line: 1-indexed end line inclusive (optional).
        line_numbers: If True, prefixes lines with line numbers (e.g. '12 | code').
    """
    p = validate_path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    try:
        content = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        size = p.stat().st_size
        return f"[Binary file – {_format_size(size)}]"

    lines = content.splitlines()
    total_lines = len(lines)

    # Slice line range if requested
    s = (start_line - 1) if (start_line is not None and start_line > 0) else 0
    e = end_line if (end_line is not None and end_line > 0) else total_lines
    s = min(s, total_lines)
    e = min(max(s, e), total_lines)

    # Large file guard: if unconstrained and file is > 2500 lines, truncate safely
    is_truncated = False
    if start_line is None and end_line is None and total_lines > 2500:
        lines = lines[:2000]
        e = 2000
        is_truncated = True
    else:
        lines = lines[s:e]

    if line_numbers:
        formatted = []
        width = len(str(e))
        for idx, line in enumerate(lines, start=s + 1):
            formatted.append(f"{idx:>{width}} | {line}")
        result = "\n".join(formatted)
    else:
        result = "\n".join(lines)

    if is_truncated:
        result += f"\n\n[Truncated: showing lines 1-2000 of {total_lines}. Pass start_line and end_line to inspect specific sections.]"

    return result


@mcp.tool(
    name="write_file",
    description="Write content to a file with atomic commit or append mode.",
)
def write_file(path: str, content: str, append: bool = False, atomic: bool = True) -> str:
    """Write text content to a file. Supports atomic writes to prevent corruption.

    Args:
        path: Relative or absolute path to the file.
        content: The text content to write.
        append: If True, appends to the file instead of overwriting.
        atomic: If True, writes to a temp file and replaces atomically.
    """
    p = validate_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if append and p.is_file():
        with open(p, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended {len(content):,} characters to {p}"

    if atomic:
        # Atomic write pattern: write to tmp file in same directory then os.replace
        tmp_fd, tmp_path = tempfile.mkstemp(dir=p.parent, prefix=".tmp_mcp_", text=True)
        try:
            with open(tmp_fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, p)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    else:
        p.write_text(content, encoding="utf-8")

    return f"Written {len(content):,} characters ({_format_size(len(content.encode('utf-8')))}) to {p}"


@mcp.tool(
    name="edit_file",
    description="Replace target string with replacement text in a file with occurrence control and diff preview.",
)
def edit_file(path: str, old_string: str, new_string: str, count: int = 0) -> str:
    """Replace occurrences of *old_string* with *new_string* in a file.

    Args:
        path: Relative or absolute path to the file.
        old_string: The exact string to find (case-sensitive, whitespace-sensitive).
        new_string: The replacement string.
        count: Number of occurrences to replace (0 = replace all, 1 = first only).
    """
    p = validate_path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    content = p.read_text(encoding="utf-8")
    if old_string not in content:
        # Check if stripped whitespace matches to give intelligent feedback
        stripped_old = old_string.strip()
        lines = content.splitlines()
        close_lines = [i + 1 for i, line in enumerate(lines) if stripped_old and stripped_old in line]
        hint = ""
        if close_lines:
            hint = f"\nHint: Similar text was found near line(s): {close_lines[:5]}. Check exact indentation and whitespace."
        raise ValueError(
            f"The specified old_string was not found in {p}.{hint}\n"
            f"Make sure you match whitespace and punctuation exactly."
        )

    total_found = content.count(old_string)
    if count > 0:
        new_content = content.replace(old_string, new_string, count)
        replaced_count = min(count, total_found)
    else:
        new_content = content.replace(old_string, new_string)
        replaced_count = total_found

    # Atomic write back
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=p.parent, prefix=".tmp_mcp_", text=True)
    try:
        with open(tmp_fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(tmp_path, p)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    return f"Successfully replaced {replaced_count} occurrence(s) in {p} (total found: {total_found})."


@mcp.tool(
    name="batch_replace",
    description="Search and replace a string across multiple files matching a glob pattern.",
)
def batch_replace(
    pattern: str,
    old_string: str,
    new_string: str,
    root_path: str = ".",
    max_files: int = 50,
) -> str:
    """Batch replace occurrences of a string across multiple files.

    Args:
        pattern: Glob pattern matching files (e.g. 'src/**/*.py', '*.ts').
        old_string: Exact text to search for.
        new_string: Replacement text.
        root_path: Base directory for search.
        max_files: Safety cap on modified files.
    """
    base = validate_path(root_path)
    matched_files = glob_module.glob(pattern, root_dir=base, recursive=True)
    modified: list[tuple[str, int]] = []

    for rel_p in matched_files:
        # Skip ignore directories
        if any(part in IGNORE_DIRS for part in Path(rel_p).parts):
            continue

        full_p = base / rel_p
        if not full_p.is_file():
            continue

        try:
            content = full_p.read_text(encoding="utf-8")
            if old_string in content:
                count = content.count(old_string)
                new_content = content.replace(old_string, new_string)
                full_p.write_text(new_content, encoding="utf-8")
                modified.append((rel_p, count))
                if len(modified) >= max_files:
                    break
        except Exception:
            continue

    if not modified:
        return f"No occurrences of '{old_string}' found in files matching '{pattern}'."

    report = [f"Batch Replace Completed across {len(modified)} file(s):"]
    for path_str, cnt in modified:
        report.append(f"- `{path_str}`: {cnt} replacement(s)")
    return "\n".join(report)


@mcp.tool(
    name="file_info",
    description="Get metadata, line count, permissions, and size for a file or directory.",
)
def file_info(path: str) -> str:
    """Inspect detailed file metadata."""
    p = validate_path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path not found: {p}")

    stat = p.stat()
    size_str = _format_size(stat.st_size)

    if p.is_file():
        try:
            lines = sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore"))
            line_info = f"{lines:,} lines"
        except Exception:
            line_info = "binary / unreadable"

        return (
            f"Path: {p}\n"
            f"Type: File\n"
            f"Size: {size_str} ({stat.st_size:,} bytes)\n"
            f"Lines: {line_info}\n"
            f"Mode: {oct(stat.st_mode)[-3:]}\n"
            f"Last Modified: {stat.st_mtime}"
        )
    elif p.is_dir():
        items = list(p.iterdir())
        return (
            f"Path: {p}\n"
            f"Type: Directory\n"
            f"Total Entries: {len(items)}\n"
            f"Mode: {oct(stat.st_mode)[-3:]}\n"
            f"Last Modified: {stat.st_mtime}"
        )
    return f"Path: {p} (Special)"


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


@mcp.tool(
    name="list_directory",
    description="List files and directories inside a given directory with size and clean filtering.",
)
def list_directory(path: str, include_hidden: bool = False) -> str:
    """List all entries in a directory with file sizes and statistics.

    Args:
        path: Relative or absolute path to the directory.
        include_hidden: If True, includes hidden and build directories (.git, node_modules, etc.).
    """
    p = validate_path(path)
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {p}")

    entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    lines: list[str] = []
    dir_count = 0
    file_count = 0
    total_size = 0

    for entry in entries:
        if not include_hidden:
            if entry.name.startswith(".") or entry.name in IGNORE_DIRS:
                continue

        if entry.is_dir():
            dir_count += 1
            lines.append(f"📁 {entry.name}/")
        else:
            file_count += 1
            try:
                size = entry.stat().st_size
                total_size += size
                lines.append(f"📄 {entry.name:<30}  {_format_size(size):>10}")
            except OSError:
                lines.append(f"📄 {entry.name}")

    summary = f"\n[{dir_count} directories, {file_count} files | Total: {_format_size(total_size)}]"
    return "\n".join(lines) + summary if lines else f"Empty directory: {p}"


@mcp.tool(
    name="glob_files",
    description="Find files matching a glob pattern (e.g. '**/*.ts', 'src/**/*.py') with automatic noise filtering.",
)
def glob_files(pattern: str, base_path: str = ".", include_hidden: bool = False) -> str:
    """Search for files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g. '**/*.py', 'src/**/*.ts', '*.json').
        base_path: Directory to search from (default: current directory).
        include_hidden: If True, includes .git, node_modules, .venv files.
    """
    base = validate_path(base_path)
    raw_matches = sorted(glob_module.glob(pattern, root_dir=base, recursive=True))

    matches: list[str] = []
    for m in raw_matches:
        if not include_hidden:
            parts = Path(m).parts
            if any(part in IGNORE_DIRS or (part.startswith(".") and part != ".") for part in parts):
                continue
        matches.append(m)

    if not matches:
        return f"No files matching '{pattern}' in {base}"

    lines = [f"Found {len(matches)} matching file(s):"]
    lines.extend(f"- {m}" for m in matches[:100])
    if len(matches) > 100:
        lines.append(f"... and {len(matches) - 100} more matches.")
    return "\n".join(lines)


@mcp.tool(description="Create one or more directories (like mkdir -p).")
def create_directory(path: str) -> str:
    """Create a directory, including any missing parents.

    Args:
        path: Relative or absolute path to the directory.
    """
    p = validate_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Created directory: {p}"
