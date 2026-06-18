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
