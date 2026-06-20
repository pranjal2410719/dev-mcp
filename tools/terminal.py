"""
Terminal command tool for dev-mcp.

Provides: run_command — execute shell commands with timeout safety.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from app import mcp
from security import validate_path


@mcp.tool(description="Run a shell command and return its output. "
    "Always set a reasonable timeout. Avoid destructive commands (rm -rf, etc.).")
def run_command(command: str, timeout_seconds: int = 60, workdir: Optional[str] = None) -> str:
    """Execute a shell command and capture stdout/stderr.

    **Security**: Avoid destructive commands. The command runs in a subprocess
    with a configurable timeout.

    Args:
        command: The shell command to run.
        timeout_seconds: Maximum seconds to wait (default 60, max 300).
        workdir: Working directory for the command (default: server CWD).
    """
    timeout = min(timeout_seconds, 300)
    cwd = validate_path(workdir) if workdir else Path.cwd()

    # Workspace Security Layer Command Auditing
    import re
    import os
    from security import get_project_root_and_safety
    
    root, safety_mode = get_project_root_and_safety()
    
    if safety_mode != "lab":
        # Block dangerous commands
        blocked_patterns = [
            r"\bsudo\b",
            r"\bmkfs\b",
            r"\bdd\b",
            r"\bshutdown\b",
            r"\breboot\b",
            r"\bpoweroff\b",
            r"\binit\s+0\b",
        ]
        
        if safety_mode == "safe":
            blocked_patterns.extend([
                r"\brm\s+-[a-zA-Z]*[rfRF]",
                r"\brm\s+--recursive",
                r"\brm\s+-d",
                r"\bgit\s+reset\s+--hard\b",
                r"\bgit\s+clean\s+-fd\b",
            ])
            
        for pattern in blocked_patterns:
            if re.search(pattern, command):
                raise PermissionError(
                    f"Command Execution Blocked: Command matches dangerous pattern '{pattern}' "
                    f"under safety mode '{safety_mode}'."
                )
                
        # Prevent path traversal
        if ".." in command:
            raise PermissionError(
                f"Command Execution Blocked: Relative path traversal '..' is forbidden "
                f"under safety mode '{safety_mode}'."
            )
            
        # Verify absolute paths used as arguments are locked to the workspace
        root_str = str(root.resolve())
        abs_paths = re.findall(r"(/[a-zA-Z0-9_\-\.\+/]+)", command)
        for p in abs_paths:
            clean_p = os.path.normpath(p)
            if clean_p.startswith(("/bin", "/usr/bin", "/usr/lib", "/lib", "/etc/alternatives", "/etc/ssl")):
                continue
            if not clean_p.startswith(root_str):
                raise PermissionError(
                    f"Command Execution Blocked: Path '{clean_p}' is outside the active workspace '{root_str}'. "
                    f"Locked under safety mode '{safety_mode}'."
                )

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
        )
        output_parts = []
        if result.stdout:
            output_parts.append(result.stdout.strip())
        if result.stderr:
            output_parts.append(f"--- stderr ---\n{result.stderr.strip()}")
        output = "\n".join(output_parts)
        status = f"[Exit code: {result.returncode}]"
        return f"{status}\n{output}" if output else status
    except subprocess.TimeoutExpired:
        return f"[Timed out after {timeout}s]"
    except Exception as e:
        return f"[Error: {e}]"
