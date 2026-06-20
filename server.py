"""
dev-mcp: A custom MCP server for managing, building, editing, and customizing projects with AI.

This is the entry-point module.  It imports the FastMCP instance from ``app``,
then imports all tool, prompt, resource, and brain modules so they register
their decorators, and finally starts the server.

Module organisation
-------------------
::

    app.py                  FastMCP instance + shared global state
    security.py             Path-validation helpers
    context.py              ProjectContext data-store class
    tools/                  10 existing generic tools
      file_ops.py           8 tools — read, write, edit, delete, list, glob, mkdir
      search.py             1 tool  — ripgrep-based code search
      terminal.py           1 tool  — shell command execution
      git_ops.py            7 tools — status, diff, log, branch, add, commit, create-branch
      context_mgmt.py      11 tools — context CRUD, tasks, decisions, project-info
    brain/                  Project Brain — project operating system
      prd_manager.py        4 tools — get/update/summarize/compare PRD
      phase_manager.py      7 tools — phase lifecycle, milestones
      todo_engine.py        7 tools — structured tasks, deps, priorities
      handoff_engine.py     3 tools — AI handoff generation
    prompts/
      definitions.py        4 prompts — overview, code-review, ADR, feature-plan
    resources/
      definitions.py        2 resources — context as JSON & Markdown
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1.  Import the FastMCP instance so it is available at module scope.
# ---------------------------------------------------------------------------
from app import mcp  # noqa: F401 — activates the instance

# ---------------------------------------------------------------------------
# 2.  Import all tool, prompt, resource, and brain modules.
#     The import itself triggers @mcp.tool / @mcp.prompt / @mcp.resource
#     decorators which register everything on the shared ``mcp`` instance.
# ---------------------------------------------------------------------------
import tools.file_ops          # noqa: F401  — 8 file-operation tools
import tools.search            # noqa: F401  — 1 code-search tool
import tools.terminal          # noqa: F401  — 1 terminal tool
import tools.git_ops           # noqa: F401  — 7 git tools
import tools.context_mgmt      # noqa: F401  — 11 context + utility tools
import brain.prd_manager       # noqa: F401  — 4 PRD tools
import brain.phase_manager     # noqa: F401  — 7 phase/milestone tools
import brain.todo_engine       # noqa: F401  — 7 task engine tools
import brain.handoff_engine    # noqa: F401  — 3 handoff tools
import brain.orchestrator      # noqa: F401  — 4 orchestration/session tools
import brain.guardian          # noqa: F401  – 1 architecture validator
import brain.dependency        # noqa: F401  — 2 dependency graph tools
import brain.sync_engine       # noqa: F401  — 3 reality sync tools
import brain.requirements      # noqa: F401  – 3 requirements traceability tools
import brain.project_readiness # noqa: F401  – 3 project onboarding tools
import prompts.definitions     # noqa: F401  — 4 prompt templates
import resources.definitions   # noqa: F401  — 2 resources

# ---------------------------------------------------------------------------
# 3.  Entry point.
# ---------------------------------------------------------------------------

import os
import sys
import subprocess
import threading

from rich.console import Console
from rich.panel import Panel
from rich.align import Align

def _print_banner() -> None:
    """Render the attractive startup banner with ASCII art and server info."""
    ascii_art = """
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│                         ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█                        │
│                         █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀                        │
│                                                                              │
│                                                                              │
│                                                                              │
│                                FastMCP 3.4.2                                 │
│                            https://gofastmcp.com                             │
│                                                                              │
│                  🖥  Server:      dev-mcp, 3.4.2                              │
│                  🚀 Deploy free: https://horizon.prefect.io                  │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
"""
    console = Console()
    panel = Panel(Align.center(ascii_art, vertical="middle"), border_style="bright_blue")
    console.print(panel)


# ── ANSI helpers (no external dep needed here) ─────────────────────────────

def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI escape code."""
    return f"\033[{code}m{text}\033[0m"


def _print_hint(still_running: bool = False) -> None:
    """Write the interactive hint line to stderr."""
    label = "Server still running" if still_running else "Server running"
    sys.stderr.write(
        f"\n  {_c('1;32', '●')} {_c('2', label)}  │  "
        f"Press {_c('1;36', '?')} for shortcut guide  "
        f"{_c('2', '·')}  "
        f"{_c('2', 'esc / q')} to stop\n\n"
    )
    sys.stderr.flush()


# ── /dev/tty key reader ────────────────────────────────────────────────────

def _read_tty_key() -> bytes:
    """
    Read one keypress directly from /dev/tty in raw mode.

    Using /dev/tty (not sys.stdin) keeps the MCP stdio channel clean —
    the server thread can read/write stdin/stdout without interference.
    Returns raw bytes; escape sequences arrive as multi-byte sequences.
    """
    import termios, tty as _tty

    fd = os.open("/dev/tty", os.O_RDONLY | os.O_NOCTTY)
    old = termios.tcgetattr(fd)
    try:
        _tty.setraw(fd)
        ch = os.read(fd, 3)   # up to 3 bytes (covers ESC sequences)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        os.close(fd)
    return ch


# ── Parallel interactive shell ─────────────────────────────────────────────

def _interactive_shell() -> None:
    """
    Runs in the main thread while the MCP server runs in a daemon thread.

    Loop:
      • Show hint line
      • Wait for a keypress on /dev/tty
        – '?' / 'h' / '/'  →  open cli.py, resume loop on exit
        – ESC / 'q' / ^C   →  print goodbye and os._exit(0)
        – anything else    →  ignore, loop again
    """
    _print_hint(still_running=False)

    guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli.py")
    _print_banner()  # Show enhanced banner before hint

    while True:
        try:
            key = _read_tty_key()
        except (KeyboardInterrupt, EOFError, OSError):
            break

        if key in (b"?", b"h", b"/"):
            # ── Open the guide; server keeps running in its thread ──────
            subprocess.run([sys.executable, guide], check=False)
            # User pressed ESC inside cli.py → came back here
            _print_hint(still_running=True)

        elif key in (
            b"\x1b",        # ESC
            b"q", b"Q",
            b"\x03",        # Ctrl+C
            b"\x04",        # Ctrl+D
        ):
            break

        # any other key → silently ignore, stay in loop

    # ── Graceful exit ────────────────────────────────────────────────────
    sys.stderr.write(
        f"\n  {_c('2', 'Server stopped.')}  "
        f"Run {_c('1', 'python server.py')} to restart.\n\n"
    )
    sys.stderr.flush()
    os._exit(0)   # kill the daemon server thread cleanly


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    """
    Start the dev-mcp MCP server.

    • Non-interactive (stdin is a pipe / MCP client connected):
        Calls mcp.run() directly — zero overhead, zero interference.

    • Interactive (human running the script in a terminal):
        Starts mcp.run() in a daemon thread, then enters a keypress
        loop on /dev/tty so the user can press '?' to open the guide
        or ESC/q to stop the server — all without touching stdio.
    """
    if not sys.stdin.isatty():
        # MCP client is connected via pipe — run cleanly with no extras.
        mcp.run()
        return

    # ── Interactive mode ─────────────────────────────────────────────────
    # Start the MCP server in a background daemon thread.
    server_thread = threading.Thread(target=mcp.run, daemon=True, name="mcp-server")
    server_thread.start()

    # Hand control to the interactive shell (blocks until user quits).
    _interactive_shell()


if __name__ == "__main__":
    main()
