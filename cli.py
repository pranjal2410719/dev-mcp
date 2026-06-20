"""
dev-mcp CLI — interactive shortcut/help guide.

Run directly:
    python cli.py
    dev-mcp-guide          (if registered in pyproject.toml scripts)

Displays a rich, tab-navigable interface with:
  • General  — about, quick-start, config snippets
  • Commands — all 50+ MCP tools with short descriptions
  • Shortcuts — key-binding reference (mirrors Antigravity CLI style)
"""

from __future__ import annotations

import sys
import os
import textwrap
from typing import NamedTuple

# ── rich imports ──────────────────────────────────────────────────────────────
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich import box
from rich.live import Live
from rich.layout import Layout

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

SHORTCUTS = [
    ("ctrl+c, q",         "Quit / exit the guide"),
    ("←  /  →  or tab",  "Cycle between tabs"),
    ("↑  /  ↓",           "Scroll within a tab"),
    ("pgup / pgdown",     "Page up / page down"),
    ("home / end",        "Go to top / bottom"),
    ("enter",             "Confirm / select"),
    ("?",                 "Toggle this shortcuts view"),
]

ALL_SHORTCUTS = [
    # ── Navigation ────────────────────────────────
    ("←  /  →",                        "Switch tab (prev / next)"),
    ("tab",                             "Next tab"),
    ("shift+tab",                       "Previous tab"),
    ("↑  /  ↓",                        "Move up / down"),
    ("pgup, shift+↑",                  "Page up"),
    ("pgdown, shift+↓",                "Page down"),
    ("home",                            "Go to top"),
    ("end",                             "Go to bottom"),
    # ── Actions ───────────────────────────────────
    ("enter",                           "Select / confirm"),
    ("q, ctrl+c, esc",                 "Quit / go back"),
    ("?",                               "Toggle shortcuts overlay"),
    # ── Display ───────────────────────────────────
    ("ctrl+l",                          "Clear / refresh screen"),
    ("ctrl+r",                          "Reload / refresh content"),
    # ── Clipboard ─────────────────────────────────
    ("ctrl+v",                          "Paste into prompt"),
    ("ctrl+y",                          "Yank (copy selection)"),
    # ── Text editing (if interactive prompt) ──────
    ("alt+enter, shift+enter",         "Insert newline in prompt"),
    ("ctrl+_, ctrl+shift+-",           "Undo last edit"),
    ("ctrl+shift+z",                    "Redo last edit"),
    # ── Dev-MCP specific ──────────────────────────
    ("ctrl+p",                          "Project dashboard overview"),
    ("ctrl+t",                          "List active tasks"),
    ("ctrl+b",                          "Build dependency graph"),
    ("ctrl+h",                          "Generate handoff document"),
    ("ctrl+g",                          "Open PRD / goal in $EDITOR"),
    ("ctrl+d",                          "Exit dev-mcp CLI"),
    ("ctrl+o",                          "Toggle tool output view"),
    ("ctrl+k",                          "Skip / approve fast"),
    ("ctrl+z",                          "Suspend CLI to shell"),
]

COMMANDS: list[tuple[str, str, str]] = [
    # category, tool name, description
    # ── File Operations ───────────────────────────
    ("File Ops",    "read_file",              "Read a file's contents"),
    ("File Ops",    "write_file",             "Write / overwrite a file"),
    ("File Ops",    "edit_file",              "Patch specific lines in a file"),
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
    # ── Commit / Prepare ──────────────────────────
    ("Brain/Commit","prepare_commit",         "Prepare commit message & diff"),
    ("Brain/Commit","commit_changes",         "Commit via brain engine"),
    # ── Utilities ─────────────────────────────────
    ("Util",        "doctor",                 "Health-check the MCP server"),
    ("Util",        "reset_project_brain",    "Reset the project brain store"),
    ("Util",        "archive_project_brain",  "Archive project brain snapshot"),
]

GENERAL_SECTIONS = [
    (
        "🚀  What is dev-mcp?",
        textwrap.dedent("""\
        dev-mcp is a [bold cyan]Model Context Protocol (MCP) server[/bold cyan] built with
        [bold]FastMCP 2+[/bold] that gives any AI assistant (Claude, Gemini, Cursor, etc.)
        a full project-management operating system — context, tasks, PRD, phases,
        git, file-ops, architecture validation, and session handoffs — all in one
        unified server.\
        """),
    ),
    (
        "⚙️  Quick start (stdio)",
        textwrap.dedent("""\
        [dim]# 1. Install[/dim]
        [bold green]pip install -e .[/bold green]   [dim]# or: uv pip install -e .[/dim]

        [dim]# 2. Run the MCP server (stdio transport — default)[/dim]
        [bold green]python server.py[/bold green]
        [dim]   — or —[/dim]
        [bold green]dev-mcp[/bold green]   [dim](after pip install)[/dim]

        [dim]# 3. Connect from your AI client[/dim]
        Point Claude / Cursor / Windsurf at the stdio process above.\
        """),
    ),
    (
        "🔌  Claude Desktop config snippet",
        textwrap.dedent("""\
        [dim]# ~/Library/Application Support/Claude/claude_desktop_config.json[/dim]
        [bold yellow]{[/bold yellow]
          [bold yellow]"mcpServers"[/bold yellow]: {
            [bold yellow]"dev-mcp"[/bold yellow]: {
              [bold yellow]"command"[/bold yellow]: [bold green]"python"[/bold green],
              [bold yellow]"args"[/bold yellow]: [[bold green]"/path/to/dev-mcp/server.py"[/bold green]]
            }
          }
        [bold yellow]}[/bold yellow]\
        """),
    ),
    (
        "📦  Transport options",
        textwrap.dedent("""\
        [bold]stdio[/bold]   (default) — pipe-based, zero config, local use
        [bold]sse[/bold]     — HTTP Server-Sent Events, for remote / browser clients
        [bold]ws[/bold]      — WebSocket transport

        Set [bold cyan]FASTMCP_TRANSPORT[/bold cyan] env var or pass [bold]--transport[/bold]
        when using the FastMCP CLI runner.\
        """),
    ),
    (
        "📚  Useful links",
        textwrap.dedent("""\
        • [link=https://github.com/pranjal2410719/dev-mcp]GitHub repo[/link]             github.com/pranjal2410719/dev-mcp
        • [link=https://gofastmcp.com]FastMCP docs[/link]            gofastmcp.com
        • [link=https://modelcontextprotocol.io]MCP spec[/link]                 modelcontextprotocol.io\
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


def _header(active_tab: int) -> Text:
    """Render the top bar with tab indicators."""
    line = Text()
    line.append("  dev-mcp  ", style="bold white on #0d3b5e")
    for i, name in enumerate(TABS):
        if i == active_tab:
            line.append(f"  {name}  ", style=TAB_ACT)
        else:
            line.append(f"  {name}  ", style=TAB_IDLE)
    line.append("  (←/→ or tab to cycle)", style=DIM)
    return line


def _footer() -> Text:
    line = Text()
    line.append("  Keyboard: ", style=DIM)
    line.append("↑/↓", style=ACCENT)
    line.append(" Navigate  ", style=DIM)
    line.append("←/→", style=ACCENT)
    line.append(" Switch Tab  ", style=DIM)
    line.append("esc", style=ACCENT)
    line.append(" Back to server  ", style=DIM)
    line.append("q", style=ACCENT)
    line.append(" Quit  ", style=DIM)
    line.append("?", style=ACCENT)
    line.append(" Shortcuts", style=DIM)
    return line


def _render_general() -> Panel:
    body = Text()
    for i, (title, content) in enumerate(GENERAL_SECTIONS):
        if i > 0:
            body.append("\n\n")
        body.append(f"  {title}\n", style=HEADING)
        body.append("  " + "─" * 60 + "\n", style=DIM)
        # render rich markup via console.render_text trick
        body.append_text(Text.from_markup("  " + content.replace("\n", "\n  ")))
    return Panel(
        body,
        title="[bold cyan]General[/bold cyan]",
        border_style=BORDER,
        padding=(1, 2),
    )


def _render_commands() -> Panel:
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        row_styles=["", "dim"],
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Category",   style="bold #5fa8d3", no_wrap=True, width=14)
    table.add_column("Tool",       style="bold green",   no_wrap=True, width=26)
    table.add_column("Description",style="white")

    prev_cat = None
    for cat, name, desc in COMMANDS:
        cat_cell = cat if cat != prev_cat else ""
        table.add_row(cat_cell, name, desc)
        prev_cat = cat

    return Panel(
        table,
        title="[bold cyan]MCP Tools[/bold cyan]",
        subtitle=f"[dim]{len(COMMANDS)} tools registered[/dim]",
        border_style=BORDER,
        padding=(0, 1),
    )


def _render_shortcuts() -> Panel:
    table = Table(
        box=box.SIMPLE,
        show_header=False,
        expand=True,
        padding=(0, 2),
    )
    table.add_column("Shortcut", style="bold cyan",  no_wrap=True, width=36)
    table.add_column("Action",   style="white")

    # Group by section markers
    sections = [
        ("Navigation",        slice(0, 8)),
        ("Actions",           slice(8, 11)),
        ("Display",           slice(11, 13)),
        ("Clipboard",         slice(13, 15)),
        ("Text Editing",      slice(15, 18)),
        ("dev-mcp Specific",  slice(18, None)),
    ]

    for section_name, sl in sections:
        table.add_row(
            Text(f"  {section_name}", style="bold yellow"),
            Text(""),
        )
        for key, action in ALL_SHORTCUTS[sl]:
            table.add_row(f"  {key}", action)
        table.add_row("", "")  # spacer

    note = Text("\n  /keybindings  to customize your shortcuts", style="dim italic")
    from rich.console import Group
    content = Group(table, note)

    return Panel(
        content,
        title="[bold cyan]Keyboard Shortcuts[/bold cyan]",
        border_style=BORDER,
        padding=(0, 1),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Static (non-interactive) renderer  — used when no terminal / readchar
# ─────────────────────────────────────────────────────────────────────────────

def render_static(tab: int = 0) -> None:
    """Print all three tabs sequentially (non-interactive fallback)."""
    console.print()
    console.print(_header(tab))
    console.print()

    if tab == 0:
        console.print(_render_general())
    elif tab == 1:
        console.print(_render_commands())
    else:
        console.print(_render_shortcuts())

    console.print(Rule(style=BORDER))
    console.print(_footer())
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Interactive (readchar) renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_interactive() -> None:
    """Full interactive mode with tab switching via arrow keys."""
    import shutil

    tab = 0
    _renders = [_render_general, _render_commands, _render_shortcuts]

    def _refresh():
        # Move cursor to top and redraw
        os.system("clear" if os.name != "nt" else "cls")
        console.print()
        console.print(_header(tab))
        console.print()
        console.print(_renders[tab]())
        console.print(Rule(style=BORDER))
        console.print(_footer())
        console.print()

    _refresh()

    while True:
        try:
            key = readchar.readkey()
        except (KeyboardInterrupt, EOFError):
            break

        if key in (readchar.key.LEFT,  "h"):
            tab = (tab - 1) % len(TABS)
            _refresh()
        elif key in (readchar.key.RIGHT, "l", "\t"):
            tab = (tab + 1) % len(TABS)
            _refresh()
        elif key in ("q", readchar.key.CTRL_C, readchar.key.ESC, readchar.key.CTRL_D):
            break
        elif key in ("?",):
            tab = 2  # jump to shortcuts tab
            _refresh()
        elif key in (readchar.key.CTRL_L,):
            _refresh()

    console.print("\n[dim]← Returning to server.  Press [bold cyan]?[/bold cyan] again to reopen this guide.[/dim]\n")


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
        # Print all three tabs for non-interactive environments
        for i in range(len(TABS)):
            render_static(i)
    else:
        try:
            render_interactive()
        except Exception:
            # Fallback gracefully
            render_static(start_tab)


if __name__ == "__main__":
    main()
