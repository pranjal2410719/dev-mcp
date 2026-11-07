"""
dev-mcp CLI — interactive shortcut/help guide.

Run directly:
    python cli.py
    dev-mcp-guide          (if registered in pyproject.toml scripts)

Displays a rich, tab-navigable, top-pinned TUI interface with:
  • General   — about, quick-start, config snippets (paginated sections)
  • Commands  — all 91 MCP tools with manual scrolling (↑/↓, PgUp/PgDn, Home/End)
  • Shortcuts — key-binding reference with manual scrolling
"""

from __future__ import annotations

import sys
import os
import shutil
import textwrap

# ── rich imports ──────────────────────────────────────────────────────────────
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box

# ── optional: readchar for key detection ─────────────────────────────────────
try:
    import readchar
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────

TABS = ["general", "commands", "shortcuts"]

FLAT_SHORTCUTS: list[tuple[str, str, str]] = [
    # Category, Key combo, Action
    ("Nav",       "←  /  →",                 "Switch tab (prev / next)"),
    ("Nav",       "tab / shift+tab",          "Cycle tabs forward / backward"),
    ("Nav",       "↑  /  ↓  or  j / k",       "Scroll up / down"),
    ("Nav",       "pgup / pgdown  (b / space)","Page up / page down"),
    ("Nav",       "home / end  (g / G)",      "Jump to top / bottom"),
    ("Actions",   "enter",                    "Select / confirm"),
    ("Actions",   "q, ctrl+c, esc",          "Quit guide / return to server"),
    ("Actions",   "?",                        "Jump to shortcuts tab"),
    ("Display",   "ctrl+l",                   "Clear & refresh screen"),
    ("Display",   "ctrl+r",                   "Reload content"),
    ("Clipboard", "ctrl+v",                   "Paste into prompt"),
    ("Clipboard", "ctrl+y",                   "Yank (copy selection)"),
    ("Editing",   "alt+enter, shift+enter",  "Insert newline in prompt"),
    ("Editing",   "ctrl+_, ctrl+shift+-",    "Undo last edit"),
    ("Editing",   "ctrl+shift+z",             "Redo last edit"),
    ("Brain",     "ctrl+p",                   "Project dashboard overview"),
    ("Brain",     "ctrl+t",                   "List active tasks"),
    ("Brain",     "ctrl+b",                   "Build dependency graph"),
    ("Brain",     "ctrl+h",                   "Generate handoff document"),
    ("Brain",     "ctrl+g",                   "Open PRD in editor"),
    ("Brain",     "ctrl+d",                   "Exit dev-mcp CLI"),
    ("Brain",     "ctrl+o",                   "Toggle tool output view"),
    ("Brain",     "ctrl+k",                   "Skip / approve fast"),
    ("Brain",     "ctrl+z",                   "Suspend CLI to shell"),
]

COMMANDS: list[tuple[str, str, str]] = [
    # Category, Tool Name, Description
    # ── File Operations ───────────────────────────
    ("File Ops",    "read_file",              "Read a file's contents"),
    ("File Ops",    "write_file",             "Write / overwrite a file"),
    ("File Ops",    "edit_file",              "Patch specific lines in a file"),
    ("File Ops",    "batch_replace",          "Atomic multi-file text replacement"),
    ("File Ops",    "file_info",              "File size, line count, permissions"),
    ("File Ops",    "delete_path",            "Delete a file or directory"),
    ("File Ops",    "delete_recursive",       "Recursively delete a directory"),
    ("File Ops",    "list_directory",         "List directory contents"),
    ("File Ops",    "glob_files",             "Find files matching a glob"),
    ("File Ops",    "create_directory",       "Create a directory (mkdir -p)"),
    # ── Search & Terminal ─────────────────────────
    ("Search",      "search_code",            "Ripgrep-based code search"),
    ("Terminal",    "run_command",            "Execute a shell command"),
    # ── Git ───────────────────────────────────────
    ("Git",         "git_status",             "Show working-tree status"),
    ("Git",         "git_diff",               "Show diffs (staged / unstaged)"),
    ("Git",         "git_log",                "Show commit history"),
    ("Git",         "git_branch",             "List / info about branches"),
    ("Git",         "git_add",                "Stage files"),
    ("Git",         "git_commit",             "Commit staged changes"),
    ("Git",         "git_create_branch",      "Create & switch to a branch"),
    ("Git",         "install_git_hooks",      "Install brain pre-commit sync hook"),
    # ── Context Management ────────────────────────
    ("Context",     "init_context",           "Initialise project context"),
    ("Context",     "get_context",            "Retrieve current context"),
    ("Context",     "update_context",         "Update context fields"),
    ("Context",     "add_to_context_list",    "Append item to a context list"),
    ("Context",     "add_key_file",           "Mark a file as key/important"),
    ("Context",     "add_task",               "Add a quick task to context"),
    ("Context",     "add_decision",           "Record an architectural decision"),
    ("Context",     "export_context_markdown","Export context as Markdown"),
    ("Context",     "remove_context_item",    "Remove an item from context"),
    ("Context",     "reset_context",          "Reset entire project context"),
    ("Context",     "project_info",           "Show project metadata"),
    # ── PRD ───────────────────────────────────────
    ("Brain/PRD",   "get_prd",                "Read the PRD document"),
    ("Brain/PRD",   "update_prd",             "Update PRD sections"),
    ("Brain/PRD",   "summarize_prd",          "Get a PRD summary"),
    ("Brain/PRD",   "compare_work_to_prd",    "Check work against PRD"),
    # ── Phase Manager ─────────────────────────────
    ("Brain/Phase", "get_current_phase",      "Get the active project phase"),
    ("Brain/Phase", "set_phase",              "Set the current phase"),
    ("Brain/Phase", "complete_phase",         "Mark current phase complete"),
    ("Brain/Phase", "next_phase",             "Advance to the next phase"),
    ("Brain/Phase", "list_phases",            "List all phases"),
    ("Brain/Phase", "add_milestone",          "Add a phase milestone"),
    ("Brain/Phase", "list_milestones",        "List all milestones"),
    # ── Task / To-Do Engine ───────────────────────
    ("Brain/Tasks", "create_task",            "Create a structured task"),
    ("Brain/Tasks", "update_task",            "Update task fields"),
    ("Brain/Tasks", "complete_task",          "Mark a task complete"),
    ("Brain/Tasks", "next_task",              "Get the next priority task"),
    ("Brain/Tasks", "blocked_tasks",          "List blocked tasks"),
    ("Brain/Tasks", "list_tasks",             "List all tasks"),
    # ── Handoff ───────────────────────────────────
    ("Brain/Handoff","generate_handoff",      "Generate AI session handoff"),
    ("Brain/Handoff","get_last_handoff",      "Retrieve last handoff doc"),
    ("Brain/Handoff","list_handoffs",         "List all handoff documents"),
    # ── Orchestration ─────────────────────────────
    ("Brain/Orch",  "generate_project_brain", "Full project-brain snapshot"),
    ("Brain/Orch",  "next_best_action",       "AI-suggested next action"),
    ("Brain/Orch",  "start_session",          "Start a work session"),
    ("Brain/Orch",  "end_session",            "End session & save summary"),
    # ── Architecture / Dependency ─────────────────
    ("Brain/Arch",  "validate_architecture",  "Validate project architecture"),
    ("Brain/Arch",  "build_dependency_graph", "Build module dependency graph"),
    ("Brain/Arch",  "impact_analysis",        "Analyse change impact"),
    # ── Sync & Verification ───────────────────────
    ("Brain/Sync",  "sync_workspace",         "Sync workspace to latest state"),
    ("Brain/Sync",  "verify_work",            "Verify work against goals"),
    ("Brain/Sync",  "project_dashboard",      "Full project health dashboard"),
    # ── Requirements ──────────────────────────────
    ("Brain/Req",   "extract_requirements",   "Extract requirements from docs"),
    ("Brain/Req",   "verify_requirements",    "Verify requirement coverage"),
    ("Brain/Req",   "verify_outcome",         "Verify outcome against req's"),
    # ── Readiness ─────────────────────────────────
    ("Brain/Ready", "assess_project_readiness","Assess project readiness"),
    ("Brain/Ready", "project_readiness_report","Generate readiness report"),
    ("Brain/Ready", "bootstrap_project",      "Bootstrap a new project"),
    ("Brain/Ready", "adopt_existing_project", "Adopt / onboard existing project"),
    ("Brain/Ready", "create_project_workspace", "Create isolated project workspace with git"),
    # ── Commit / Prepare ──────────────────────────
    ("Brain/Commit","prepare_commit",         "Prepare commit message & diff"),
    ("Brain/Commit","commit_changes",         "Commit via brain engine"),
    # ── Utilities ─────────────────────────────────
    ("Util",        "doctor",                 "Health-check the MCP server"),
    ("Util",        "reset_project_brain",    "Reset the project brain store"),
    ("Util",        "archive_project_brain",  "Archive project brain snapshot"),
    # ── Desktop Automation ────────────────────────
    ("Desktop",     "desktop_status",         "Inspect agent-desktop & AT-SPI bus"),
    ("Desktop",     "desktop_list_apps",      "List running GUI applications"),
    ("Desktop",     "desktop_list_windows",   "List desktop windows & bounds"),
    ("Desktop",     "desktop_snapshot",       "Capture accessibility tree snapshot"),
    ("Desktop",     "desktop_find",           "Find UI elements by name or role"),
    ("Desktop",     "desktop_click",          "Semantic or coordinate mouse click"),
    ("Desktop",     "desktop_type",           "Type text into target UI elements"),
    ("Desktop",     "desktop_press",          "Send keyboard shortcuts / combos"),
    ("Desktop",     "desktop_scroll",         "Scroll element or window viewport"),
    ("Desktop",     "desktop_launch",         "Launch desktop application"),
    ("Desktop",     "desktop_close_app",      "Close or terminate application"),
    ("Desktop",     "desktop_focus_window",   "Bring target window into focus"),
    ("Desktop",     "desktop_clipboard",      "Read, write, or clear clipboard"),
    ("Desktop",     "desktop_verify_element", "Assert GUI element exists and state"),
    ("Desktop",     "desktop_screenshot",     "Capture PNG screenshot of window"),
    ("Desktop",     "desktop_action",         "Universal agent-desktop dispatcher"),
    # ── Server Profile ────────────────────────────
    ("Profile",     "get_dev_mcp_profile",    "Inspect active profile & loaded tools"),
]

GENERAL_SECTIONS = [
    (
        "🚀  What is dev-mcp?",
        textwrap.dedent("""\
        dev-mcp is an [bold cyan]AI Engineering Operating System[/bold cyan] built on FastMCP.
        It equips coding assistants (Claude, Cursor, Gemini, Cline, Roo Code, Windsurf, Antigravity)
        with persistent project memory — PRD specs, task graphs, phase tracking, architecture validation,
        desktop GUI automation, and session handoffs stored directly in your workspace.\
        """),
    ),
    (
        "⚡  Quick Run & Installation",
        textwrap.dedent("""\
        [dim]# Option 1: Zero-install execution via uvx (recommended)[/dim]
        [bold green]uvx --from braynix-dev-mcp dev-mcp[/bold green]

        [dim]# Option 2: Persistent install via pip or uv tool[/dim]
        [bold green]pip install braynix-dev-mcp[/bold green]   [dim]# or: uv tool install braynix-dev-mcp[/dim]
        [bold green]dev-mcp[/bold green]

        [dim]# Option 3: Filter tools with dynamic profiles[/dim]
        [bold green]DEV_MCP_PROFILE=code dev-mcp[/bold green]       [dim]# 56 tools (code & git)[/dim]
        [bold green]DEV_MCP_PROFILE=planning dev-mcp[/bold green]   [dim]# 43 tools (PRD & tasks)[/dim]
        [bold green]DEV_MCP_PROFILE=audit dev-mcp[/bold green]      [dim]# 58 tools (security & readiness)[/dim]
        [bold green]DEV_MCP_PROFILE=desktop dev-mcp[/bold green]    [dim]# 39 tools (GUI automation)[/dim]\
        """),
    ),
    (
        "🔌  Client Configuration (Zero-Install)",
        textwrap.dedent("""\
        [dim]# In Claude Desktop or Cursor MCP settings:[/dim]
        [bold yellow]{[/bold yellow]
          [bold yellow]"mcpServers"[/bold yellow]: {
            [bold yellow]"dev-mcp"[/bold yellow]: {
              [bold yellow]"command"[/bold yellow]: [bold green]"uvx"[/bold green],
              [bold yellow]"args"[/bold yellow]: [[bold green]"--from"[/bold green], [bold green]"braynix-dev-mcp"[/bold green], [bold green]"dev-mcp"[/bold green]]
            }
          }
        [bold yellow]}[/bold yellow]\
        """),
    ),
    (
        "🛡️  Safety & Workspace Lock",
        textwrap.dedent("""\
        [bold green]safe[/bold green] (default)   — strict realpath jailing; path traversal & destructive commands blocked.
        [bold yellow]trusted[/bold yellow]        — in-bounds recursive deletions permitted for trusted pairing.
        [bold red]lab[/bold red]            — multi-directory allowlists via DEV_MCP_ALLOWED_DIRS.\
        """),
    ),
    (
        "🌐  Official Links & Documentation",
        textwrap.dedent("""\
        • [link=https://dev-mcp.me]Website & Studio[/link]      https://dev-mcp.me
        • [link=https://pypi.org/project/braynix-dev-mcp/]PyPI Package[/link]        https://pypi.org/project/braynix-dev-mcp/
        • [link=https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.pranjal2410719/dev-mcp]MCP Registry[/link]        io.github.pranjal2410719/dev-mcp
        • [link=https://github.com/pranjal2410719/dev-mcp]GitHub Repo[/link]         github.com/pranjal2410719/dev-mcp\
        """),
    ),
]

# ─────────────────────────────────────────────────────────────────────────────
# Rendering helpers
# ─────────────────────────────────────────────────────────────────────────────

ACCENT   = "bold cyan"
DIM      = "dim"
HEADING  = "bold white"
TAB_ACT  = "bold white on #1a6a8a"
TAB_IDLE = "dim on #1a1a2e"
BORDER   = "#2e4a6a"


def _get_visible_limit() -> int:
    """Calculate visible table rows based on current terminal height."""
    try:
        lines = shutil.get_terminal_size((80, 24)).lines
    except Exception:
        lines = 24
    # Chrome: 1 header line, 1 spacing, panel borders (2 lines), table header & divider (2 lines), 1 rule, 1 footer line
    return max(5, lines - 9)


def _header(active_tab: int) -> Text:
    """Render the top bar with active tab indicator."""
    line = Text()
    line.append("  dev-mcp  ", style="bold white on #0d3b5e")
    for i, name in enumerate(TABS):
        if i == active_tab:
            line.append(f"  {name}  ", style=TAB_ACT)
        else:
            line.append(f"  {name}  ", style=TAB_IDLE)
    line.append("  │  ←/→ Tab  ·  ↑/↓ Scroll  ·  esc/q Exit", style=DIM)
    return line


def _footer(tab_idx: int) -> Text:
    """Render keyboard shortcuts footer based on active tab."""
    line = Text()
    line.append("  Keyboard: ", style=DIM)
    if tab_idx == 0:
        line.append("↑/k", style=ACCENT)
        line.append(" Prev Section  ", style=DIM)
        line.append("↓/j", style=ACCENT)
        line.append(" Next Section  ", style=DIM)
    else:
        line.append("↑/k", style=ACCENT)
        line.append(" Up  ", style=DIM)
        line.append("↓/j", style=ACCENT)
        line.append(" Down  ", style=DIM)
        line.append("PgUp/PgDn", style=ACCENT)
        line.append(" Page  ", style=DIM)
    line.append("Home/End", style=ACCENT)
    line.append(" Top/End  ", style=DIM)
    line.append("←/→", style=ACCENT)
    line.append(" Switch Tab  ", style=DIM)
    line.append("esc/q", style="bold red")
    line.append(" Exit", style=DIM)
    return line


def _render_general(section_idx: int | None = 0) -> Panel:
    """Render General quickstart. If section_idx is None, render all (static)."""
    if section_idx is None:
        body = Text()
        for i, (title, content) in enumerate(GENERAL_SECTIONS):
            if i > 0:
                body.append("\n\n")
            body.append(f"  {title}\n", style=HEADING)
            body.append("  " + "─" * 60 + "\n", style=DIM)
            body.append_text(Text.from_markup("  " + content.replace("\n", "\n  ")))
        return Panel(
            body,
            title="[bold cyan]General[/bold cyan]",
            border_style=BORDER,
            padding=(1, 2),
        )

    total = len(GENERAL_SECTIONS)
    section_idx = max(0, min(section_idx, total - 1))
    title, content = GENERAL_SECTIONS[section_idx]

    dots = []
    for i in range(total):
        if i == section_idx:
            dots.append(f"[bold cyan]● {i + 1}[/bold cyan]")
        else:
            dots.append(f"[dim]○ {i + 1}[/dim]")
    dots_str = " ".join(dots)

    body = Text()
    body.append(f"\n  {title}\n", style=HEADING)
    body.append("  " + "─" * 68 + "\n\n", style=DIM)
    body.append_text(Text.from_markup("  " + content.replace("\n", "\n  ")))

    subtitle = (
        f"Section [bold white]{section_idx + 1}[/bold white] of [bold cyan]{total}[/bold cyan] ({dots_str})  │  "
        "[dim]↑/k Prev Section · ↓/j Next Section · Home/End Top/Bottom[/dim]"
    )

    return Panel(
        body,
        title="[bold cyan]General — dev-mcp Quickstart[/bold cyan]",
        subtitle=subtitle,
        border_style=BORDER,
        padding=(0, 1),
    )


def _render_commands(offset: int = 0, limit: int | None = None) -> Panel:
    """Render MCP commands list with windowed pagination."""
    total = len(COMMANDS)
    if limit is None:
        slice_end = total
        items = COMMANDS
        subtitle = f"[bold cyan]{total}[/bold cyan] tools registered"
    else:
        max_offset = max(0, total - limit)
        offset = max(0, min(offset, max_offset))
        slice_end = min(total, offset + limit)
        items = COMMANDS[offset:slice_end]
        pct = int((slice_end / total) * 100) if total else 100
        subtitle = (
            f"Showing tools [bold white]{offset + 1}–{slice_end}[/bold white] of [bold cyan]{total}[/bold cyan] ({pct}%)  │  "
            "[dim]↑/k Up · ↓/j Down · PgUp/PgDn · Home/End[/dim]"
        )

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        row_styles=["", "dim"],
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#",          style="dim",          no_wrap=True, width=4, justify="right")
    table.add_column("Category",   style="bold #5fa8d3", no_wrap=True, width=13)
    table.add_column("Tool",       style="bold green",   no_wrap=True, width=24)
    table.add_column("Description",style="white",        no_wrap=True, overflow="ellipsis")

    prev_cat = None
    start_idx = offset + 1 if limit is not None else 1
    for idx, (cat, name, desc) in enumerate(items, start=start_idx):
        cat_cell = cat if cat != prev_cat else ""
        table.add_row(str(idx), cat_cell, name, desc)
        prev_cat = cat

    return Panel(
        table,
        title="[bold cyan]MCP Tools[/bold cyan]",
        subtitle=subtitle,
        border_style=BORDER,
        padding=(0, 0),
    )


def _render_shortcuts(offset: int = 0, limit: int | None = None) -> Panel:
    """Render shortcuts reference with windowed pagination."""
    total = len(FLAT_SHORTCUTS)
    if limit is None:
        slice_end = total
        items = FLAT_SHORTCUTS
        subtitle = f"[bold cyan]{total}[/bold cyan] shortcuts configured"
    else:
        max_offset = max(0, total - limit)
        offset = max(0, min(offset, max_offset))
        slice_end = min(total, offset + limit)
        items = FLAT_SHORTCUTS[offset:slice_end]
        pct = int((slice_end / total) * 100) if total else 100
        subtitle = (
            f"Showing shortcuts [bold white]{offset + 1}–{slice_end}[/bold white] of [bold cyan]{total}[/bold cyan] ({pct}%)  │  "
            "[dim]↑/k Up · ↓/j Down · PgUp/PgDn · Home/End[/dim]"
        )

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        row_styles=["", "dim"],
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#",        style="dim",          no_wrap=True, width=4, justify="right")
    table.add_column("Category", style="bold #5fa8d3", no_wrap=True, width=12)
    table.add_column("Shortcut", style="bold cyan",    no_wrap=True, width=26)
    table.add_column("Action",   style="white",        no_wrap=True, overflow="ellipsis")

    prev_cat = None
    start_idx = offset + 1 if limit is not None else 1
    for idx, (cat, key, action) in enumerate(items, start=start_idx):
        cat_cell = cat if cat != prev_cat else ""
        table.add_row(str(idx), cat_cell, key, action)
        prev_cat = cat

    return Panel(
        table,
        title="[bold cyan]Keyboard Shortcuts[/bold cyan]",
        subtitle=subtitle,
        border_style=BORDER,
        padding=(0, 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Static (non-interactive) renderer — used when no terminal / piped
# ─────────────────────────────────────────────────────────────────────────────

def render_static(tab: int = 0) -> None:
    """Print tab content sequentially (non-interactive fallback)."""
    console.print()
    console.print(_header(tab))
    console.print()

    if tab == 0:
        console.print(_render_general(None))
    elif tab == 1:
        console.print(_render_commands(limit=None))
    else:
        console.print(_render_shortcuts(limit=None))

    console.print(Rule(style=BORDER))
    console.print(_footer(tab))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Interactive TUI renderer — starts pinned at the top, scrollable by user
# ─────────────────────────────────────────────────────────────────────────────

def render_interactive(start_tab: int = 0) -> None:
    """Interactive TUI mode pinned to top of terminal with manual scrolling."""
    tab = start_tab
    offsets: dict[int, int] = {0: 0, 1: 0, 2: 0}

    def _refresh() -> None:
        console.clear()
        limit = _get_visible_limit()
        console.print(_header(tab))

        if tab == 0:
            console.print(_render_general(offsets[0]))
        elif tab == 1:
            console.print(_render_commands(offsets[1], limit=limit))
        else:
            console.print(_render_shortcuts(offsets[2], limit=limit))

        console.print(Rule(style=BORDER))
        console.print(_footer(tab))

    _refresh()

    while True:
        try:
            key = readchar.readkey()
        except (KeyboardInterrupt, EOFError):
            break

        limit = _get_visible_limit()

        # ── Exit ──────────────────────────────────────────────
        if key in ("q", "Q", readchar.key.ESC, readchar.key.CTRL_C, readchar.key.CTRL_D):
            break

        # ── Up / Previous ─────────────────────────────────────
        elif key in (readchar.key.UP, "k", "\x1b[A", "\x1bOA"):
            offsets[tab] = max(0, offsets[tab] - 1)
            _refresh()

        # ── Down / Next ───────────────────────────────────────
        elif key in (readchar.key.DOWN, "j", "\x1b[B", "\x1bOB"):
            if tab == 0:
                offsets[0] = min(len(GENERAL_SECTIONS) - 1, offsets[0] + 1)
            elif tab == 1:
                max_off = max(0, len(COMMANDS) - limit)
                offsets[1] = min(max_off, offsets[1] + 1)
            elif tab == 2:
                max_off = max(0, len(FLAT_SHORTCUTS) - limit)
                offsets[2] = min(max_off, offsets[2] + 1)
            _refresh()

        # ── Page Down ─────────────────────────────────────────
        elif key in (readchar.key.PAGE_DOWN, readchar.key.SPACE, " ", "f", "\x1b[6~"):
            if tab == 0:
                offsets[0] = min(len(GENERAL_SECTIONS) - 1, offsets[0] + 1)
            elif tab == 1:
                max_off = max(0, len(COMMANDS) - limit)
                offsets[1] = min(max_off, offsets[1] + limit)
            elif tab == 2:
                max_off = max(0, len(FLAT_SHORTCUTS) - limit)
                offsets[2] = min(max_off, offsets[2] + limit)
            _refresh()

        # ── Page Up ───────────────────────────────────────────
        elif key in (readchar.key.PAGE_UP, "b", "\x1b[5~"):
            if tab == 0:
                offsets[0] = max(0, offsets[0] - 1)
            else:
                offsets[tab] = max(0, offsets[tab] - limit)
            _refresh()

        # ── Jump to Top (Home / g) ────────────────────────────
        elif key in (readchar.key.HOME, "g", "\x1b[H", "\x1b[1~", "\x1b[7~", "\x1bOH"):
            offsets[tab] = 0
            _refresh()

        # ── Jump to Bottom (End / G) ──────────────────────────
        elif key in (readchar.key.END, "G", "\x1b[F", "\x1b[4~", "\x1b[8~", "\x1bOF"):
            if tab == 0:
                offsets[0] = len(GENERAL_SECTIONS) - 1
            elif tab == 1:
                offsets[1] = max(0, len(COMMANDS) - limit)
            elif tab == 2:
                offsets[2] = max(0, len(FLAT_SHORTCUTS) - limit)
            _refresh()

        # ── Next Tab ──────────────────────────────────────────
        elif key in (readchar.key.RIGHT, "l", readchar.key.TAB, "\t", "\x1b[C", "\x1bOC"):
            tab = (tab + 1) % len(TABS)
            _refresh()

        # ── Previous Tab ──────────────────────────────────────
        elif key in (readchar.key.LEFT, "h", readchar.key.SHIFT_TAB, "\x1b[Z", "\x1b[D", "\x1bOD"):
            tab = (tab - 1) % len(TABS)
            _refresh()

        # ── Shortcuts Direct Access ───────────────────────────
        elif key == "?":
            tab = 2
            _refresh()

        # ── Refresh Screen ────────────────────────────────────
        elif key == readchar.key.CTRL_L:
            _refresh()

    console.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for the dev-mcp shortcut guide CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="dev-mcp-guide",
        description="dev-mcp shortcut & command reference guide",
    )
    parser.add_argument(
        "--tab", "-t",
        choices=TABS,
        default="general",
        help="Starting tab (default: general)",
    )
    parser.add_argument(
        "--no-interactive", "-n",
        action="store_true",
        help="Print tab content without interactive controls",
    )
    args = parser.parse_args()

    start_tab = TABS.index(args.tab)

    if args.no_interactive or not sys.stdout.isatty() or not HAS_READCHAR:
        # Print tab for non-interactive environments
        render_static(start_tab)
    else:
        try:
            render_interactive(start_tab=start_tab)
        except Exception:
            render_static(start_tab)


if __name__ == "__main__":
    main()
