# 🚀 dev-mcp v2.2.2 Release Notes

**Release Date:** November 2026  
**Status:** Interactive TUI & Viewport Fix Release  
**Package Identity:** `braynix-dev-mcp` (PyPI) / `io.github.pranjal2410719/dev-mcp` (MCP Registry)  
**Total MCP Tools:** 91 Tools (18 Modules)  
**Transport:** Stdio (pure JSON-RPC)  

---

## 🌟 Executive Summary

`dev-mcp` version **2.2.2** resolves viewport auto-scrolling issues in the interactive CLI guide (`dev-mcp-guide`) and startup overlay, ensuring the terminal interface stays pinned to the top of the terminal screen upon launch and is scrolled manually by the student or developer.

Additionally, this release incorporates Python 3.10 and 3.11 backward compatibility fixes from v2.2.1, eliminates duplicate FastMCP startup banner noise, and refines keyboard navigation.

---

## ⚡ Key Highlights of v2.2.2 & v2.2.1

### 1. Top-Pinned Interactive TUI (`cli.py`)
* **Dynamic Terminal Height Budgeting**:
  - Dynamically detects terminal dimensions using `shutil.get_terminal_size()`.
  - Windows table rows to `max(5, lines - 9)` to strictly prevent output from overflowing the terminal buffer and forcing the cursor down.
  - Every tab always begins pinned at **Row 1 / Tool #1 / Section 1**.
* **Manual Windowed Scrolling**:
  - <kbd>↑</kbd> / <kbd>k</kbd>: Move up one tool / previous section.
  - <kbd>↓</kbd> / <kbd>j</kbd>: Move down one tool / next section.
  - <kbd>PgUp</kbd> / <kbd>b</kbd>: Page up by a full viewport.
  - <kbd>PgDn</kbd> / <kbd>Space</kbd> / <kbd>f</kbd>: Page down by a full viewport.
  - <kbd>Home</kbd> / <kbd>g</kbd>: Jump immediately to the top (Tool #1 / Section 1).
  - <kbd>End</kbd> / <kbd>G</kbd>: Jump to the bottom.
  - <kbd>←</kbd> / <kbd>→</kbd> or <kbd>Tab</kbd> / <kbd>Shift+Tab</kbd>: Switch tabs.
  - <kbd>?</kbd>: Direct jump to keyboard shortcuts reference.
  - <kbd>esc</kbd> / <kbd>q</kbd>: Cleanly exit and restore terminal state.
* **General Tab Section Pagination**:
  - Paginates the 5 General overview sections (`What is dev-mcp?`, `Quick Run & Installation`, `Client Configuration`, `Safety & Workspace Lock`, `Official Links & Docs`) with live dot progress indicators (`● 1  ○ 2  ○ 3  ○ 4  ○ 5`), eliminating vertical spillover.
* **Real-Time Progress Indicators**:
  - Panel subtitles dynamically report progress:  
    `Showing tools 1–15 of 91 tools (16%) │ ↑/k Up · ↓/j Down · PgUp/PgDn · Home/End`

### 2. Python 3.10 / 3.11 Backward Compatibility (v2.2.1)
* **Nested F-String Fix in `tools/git_ops.py`**:
  - Resolved `SyntaxError: unexpected character after line continuation character` occurring in Python 3.10 and 3.11 runtimes by pre-joining output lines before string formatting.

### 3. Server Startup Banner Purity (`server.py`)
* **Suppressed Duplicate FastMCP Banner**:
  - Enabled `show_banner=False` in `mcp.run()` call to prevent FastMCP's internal unstyled box and update notifications from cluttering stderr.
* **Unified Diagnostic Panel**:
  - Clean Rich Grid panel displaying server status, active profile, tool count, PyPI distribution package, and documentation URL.
  - Automatically clears terminal via `console.clear()` when running in an interactive tty, keeping the banner positioned at row 1.

---

## 🛠️ Verification & Installation

### Zero-Install Execution
```bash
uvx --from braynix-dev-mcp dev-mcp
```

### Persistent Installation
```bash
pip install --upgrade braynix-dev-mcp
# or:
uv tool install --force braynix-dev-mcp
```

### Test Interactive Guide
```bash
dev-mcp-guide
```
*The guide will open pinned at the top on Section 1 and Tool #1.*
