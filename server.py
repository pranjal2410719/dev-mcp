"""
dev-mcp: A custom MCP server for managing, building, editing, and customizing projects with AI.

This is the entry-point module.  It imports the FastMCP instance from ``app``,
then imports all tool, prompt, resource, and brain modules so they register
their decorators (91 registered tools, 2 resources, and 4 prompts across 18 modules),
and finally starts the server.

Module organisation
-------------------
::

    app.py                  FastMCP instance + shared global state
    security.py             Path-validation helpers & workspace lock
    context.py              ProjectContext data-store class
    tools/                  48 tools across 7 modules
      file_ops.py          10 tools — read, write, edit, batch_replace, file_info, delete, list, glob, mkdir
      search.py             1 tool  — ripgrep-based code search with regex fallback
      terminal.py           1 tool  — sandboxed shell command execution
      git_ops.py            8 tools — status, diff, log, branch, add, commit, create-branch, install_git_hooks
      context_mgmt.py      11 tools — context CRUD, tasks, decisions, project-info
      desktop_ops.py       16 tools — GUI snapshot, element finding, clicking, typing, shortcuts, window control
      profile.py            1 tool  — get_dev_mcp_profile active profile inspection
    brain/                  Project Brain — 43 tools across 10 modules
      prd_manager.py        4 tools — get/update/summarize/compare PRD
      phase_manager.py      7 tools — phase lifecycle, milestones
      todo_engine.py        6 tools — structured tasks, deps, priorities
      handoff_engine.py     3 tools — AI handoff generation
      orchestrator.py       6 tools — session lifecycle, project brain, commit flow
      guardian.py           1 tool  — architectural rule validation
      dependency.py         2 tools — cached AST dependency graph & blast radius impact analysis
      sync_engine.py        3 tools — git reality sync, task verification, dashboard
      requirements.py       3 tools — PRD requirement extraction, verification & outcome audit
      project_readiness.py  8 tools — onboarding maturity, doctor, workspace creation
    prompts/
      definitions.py        4 prompts — overview, code-review, ADR, feature-plan
    resources/
      definitions.py        2 resources — context as JSON & Markdown
"""

from __future__ import annotations

import os
import sys
import importlib

# ---------------------------------------------------------------------------
# 1.  Import the FastMCP instance so it is available at module scope.
# ---------------------------------------------------------------------------
from app import mcp  # noqa: F401 — activates the instance

# ---------------------------------------------------------------------------
# 2.  Tool Profiles & Dynamic Module Registration
#     Allows filtering tools via DEV_MCP_PROFILE to dramatically reduce
#     LLM token consumption (e.g., DEV_MCP_PROFILE=code|planning|audit|desktop|all).
# ---------------------------------------------------------------------------
import importlib

PROFILE_MODULES = {
    "code": [
        "tools.file_ops",
        "tools.search",
        "tools.terminal",
        "tools.git_ops",
        "tools.context_mgmt",
        "brain.dependency",
        "brain.orchestrator",
        "prompts.definitions",
        "resources.definitions",
    ],
    "planning": [
        "brain.prd_manager",
        "brain.phase_manager",
        "brain.todo_engine",
        "brain.requirements",
        "brain.project_readiness",
        "brain.handoff_engine",
        "tools.context_mgmt",
        "prompts.definitions",
        "resources.definitions",
    ],
    "audit": [
        "brain.sync_engine",
        "brain.guardian",
        "brain.dependency",
        "brain.requirements",
        "brain.project_readiness",
        "tools.git_ops",
        "tools.desktop_ops",
        "prompts.definitions",
        "resources.definitions",
    ],
    "desktop": [
        "tools.desktop_ops",
        "tools.file_ops",
        "tools.terminal",
        "tools.context_mgmt",
        "prompts.definitions",
        "resources.definitions",
    ],
    "all": [
        "tools.file_ops",
        "tools.search",
        "tools.terminal",
        "tools.git_ops",
        "tools.context_mgmt",
        "tools.desktop_ops",
        "brain.prd_manager",
        "brain.phase_manager",
        "brain.todo_engine",
        "brain.handoff_engine",
        "brain.orchestrator",
        "brain.guardian",
        "brain.dependency",
        "brain.sync_engine",
        "brain.requirements",
        "brain.project_readiness",
        "prompts.definitions",
        "resources.definitions",
    ],
}


def _resolve_profile_modules() -> tuple[str, list[str]]:
    profile_env = os.environ.get("DEV_MCP_PROFILE", "all").lower().strip()
    if profile_env in PROFILE_MODULES:
        return profile_env, PROFILE_MODULES[profile_env]

    selected_modules = set()
    parts = [p.strip() for p in profile_env.split(",") if p.strip()]
    for part in parts:
        if part in PROFILE_MODULES:
            selected_modules.update(PROFILE_MODULES[part])
        elif part.startswith("tools.") or part.startswith("brain."):
            selected_modules.add(part)

    if selected_modules:
        selected_modules.add("prompts.definitions")
        selected_modules.add("resources.definitions")
        return profile_env, sorted(list(selected_modules))

    return "all", PROFILE_MODULES["all"]


ACTIVE_PROFILE, MODULES_TO_LOAD = _resolve_profile_modules()
LOADED_MODULES: list[str] = []

for mod_name in MODULES_TO_LOAD:
    try:
        importlib.import_module(mod_name)
        LOADED_MODULES.append(mod_name)
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to import {mod_name}: {e}\n")


@mcp.tool(
    name="get_dev_mcp_profile",
    description="Get the active dev-mcp tool profile and registered module count.",
)
def get_dev_mcp_profile() -> str:
    """Return active profile name and registered module list."""
    return f"Active dev-mcp Profile: '{ACTIVE_PROFILE}' (loaded {len(LOADED_MODULES)} modules: {', '.join(LOADED_MODULES)})."


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
from rich.table import Table


def _print_banner() -> None:
    """Render the attractive startup banner with server info to stderr."""
    console = Console(stderr=True)
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan", justify="right")
    grid.add_column(style="white")

    grid.add_row("Status:", "[bold green]● Running[/bold green] (stdio transport)")
    grid.add_row("Profile:", f"[bold white]{ACTIVE_PROFILE}[/bold white] [dim]({len(LOADED_MODULES)} modules · 91 tools)[/dim]")
    grid.add_row("Workspace:", "[dim]Jailed Lock Active[/dim] · Mode: [bold]safe[/bold]")
    grid.add_row("Distribution:", "PyPI: [bold green]braynix-dev-mcp[/bold green] · Registry: [bold blue]io.github.pranjal2410719/dev-mcp[/bold blue]")
    grid.add_row("Docs & Web:", "[link=https://dev-mcp.me]https://dev-mcp.me[/link]")

    panel = Panel(
        grid,
        title="[bold white]🧠 dev-mcp [cyan]v2.2.1[/cyan][/bold white] [dim]— AI Engineering Operating System[/dim]",
        title_align="left",
        subtitle="[dim]Press [bold cyan]?[/bold cyan] for Interactive Guide · [bold red]q[/bold red] to stop[/dim]",
        subtitle_align="right",
        border_style="bright_blue",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()


# ── ANSI helpers (no external dep needed here) ─────────────────────────────

def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI escape code."""
    return f"\033[{code}m{text}\033[0m"


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
      • Show enhanced dev-mcp banner
      • Wait for a keypress on /dev/tty
        – '?' / 'h' / '/'  →  open interactive guide, resume loop on exit
        – ESC / 'q' / ^C   →  print goodbye and os._exit(0)
        – anything else    →  ignore, loop again
    """
    _print_banner()

    while True:
        try:
            key = _read_tty_key()
        except (KeyboardInterrupt, EOFError, OSError):
            break

        if key in (b"?", b"h", b"/"):
            try:
                from cli import main as cli_main
                cli_main()
            except Exception as err:
                sys.stderr.write(f"Error launching guide: {err}\n")
            _print_banner()

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
        f"Run {_c('1', 'dev-mcp')} to restart.\n\n"
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
        mcp.run(show_banner=False)
        return

    # ── Interactive mode ─────────────────────────────────────────────────
    # Start the MCP server in a background daemon thread with show_banner=False
    # so FastMCP does not double-print a duplicate unstyled box.
    server_thread = threading.Thread(
        target=lambda: mcp.run(show_banner=False),
        daemon=True,
        name="mcp-server",
    )
    server_thread.start()

    # Hand control to the interactive shell (blocks until user quits).
    _interactive_shell()


if __name__ == "__main__":
    main()
