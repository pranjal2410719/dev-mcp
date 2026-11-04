# 🚀 dev-mcp v2.1.0 Release Notes

**Release Date:** November 2026  
**Status:** Stable Production Release  
**Total MCP Tools:** 84 Tools (18 Modules)  
**Safety Modes:** `safe` (default), `trusted`, `lab`

---

## 🌟 Executive Summary

`dev-mcp` version **2.1.0** introduces a breakthrough leap in AI Agent engineering performance, responsiveness, and operating system integration. This release transforms `dev-mcp` from a backend-only technical project manager into a complete **full-stack and desktop-aware AI Engineering OS**.

### Key Highlights of v2.1.0:
1. **Dynamic Tool Profiling (`DEV_MCP_PROFILE`)**:
   - Reduces initial system prompt LLM token overhead by **up to 75%**.
   - Profile modes: `code`, `planning`, `audit`, `desktop`, and `all` (default).
2. **agent-desktop GUI Integration (Linux AT-SPI / X11 / Wayland)**:
   - 9 new desktop automation and inspection tools (`desktop_status`, `desktop_list_apps`, `desktop_list_windows`, `desktop_snapshot`, `desktop_find`, `desktop_click`, `desktop_type`, `desktop_verify_element`, `desktop_screenshot`).
   - Enables end-to-end multi-modal and GUI accessibility tree verification for native desktop apps, browsers, and terminals.
3. **High-Performance Filesystem & Search Overhaul**:
   - Up to **26.2× faster** path validation in `security.py` by eliminating expensive stack traces on standard operations.
   - Sliced file reads (`start_line`, `end_line`) with line numbering options and large-file truncation protection (>2,500 lines).
   - Atomic writes (`write_file` with temporary files and atomic `os.replace`) to prevent corrupted states.
   - In-place surgical string editing with `count` parameter and fuzzy whitespace mismatch hints.
   - Batch multi-file refactoring (`batch_replace`).
   - File metadata inspection (`file_info`).
   - Automatic noise directory exclusion (`.git`, `node_modules`, `__pycache__`, `.venv`, `.next`, `dist`, `build`) for `list_directory` and `glob_files`.
   - Native Ripgrep (`rg`) integration in `search_code` with automatic Python regex fallback and context lines support.
4. **AST Dependency Graph & Blast-Radius Caching**:
   - Fast `mtime`-based in-memory caching (`_FILE_PARSE_CACHE`) in `brain/dependency.py`.
   - Sub-millisecond `impact_analysis` re-runs on large codebases (>500 files).
   - Automated risk scoring (Low, Medium, High) and test suite isolation.
5. **Automated Git Hook Sync (`install_git_hooks`)**:
   - Pre-commit hook generation to keep `.project_brain` and `.project-context.json` automatically in sync with developer commits.

---

## 🛠️ Complete Catalog of New Tools in v2.1.0

### 1. Desktop GUI Automation (`tools/desktop_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `desktop_status` | None | Verify CLI availability, platform, and OS accessibility permissions. |
| `desktop_list_apps` | None | List running applications with process names and window titles. |
| `desktop_list_windows` | None | Enumerate active desktop windows and their geometries. |
| `desktop_snapshot` | `app: str = ""` | Capture hierarchical accessibility tree state (JSON/YAML). |
| `desktop_find` | `name: str = ""`, `role: str = ""`, `app: str = ""` | Query specific UI nodes (buttons, inputs, labels) in the UI tree. |
| `desktop_click` | `name: str = ""`, `role: str = ""`, `app: str = ""` | Simulate native mouse click on a matching desktop element. |
| `desktop_type` | `text: str`, `app: str = ""` | Send native keyboard input into active element or specified application. |
| `desktop_verify_element` | `name: str`, `role: str = ""`, `app: str = ""` | Assert that an expected element exists and is visible on desktop. |
| `desktop_screenshot` | `output_path: str = "screenshot.png"` | Capture high-resolution desktop display screenshot. |

### 2. Filesystem & Refactoring (`tools/file_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `batch_replace` | `file_paths: list[str]`, `old_string: str`, `new_string: str` | Perform atomic multi-file replacements in a single transaction. |
| `file_info` | `path: str` | Retrieve file size, line count, modified time, and permissions. |

### 3. Server Optimization & Profiling (`server.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `get_dev_mcp_profile` | None | Query active profile, loaded module count, and active tools. |

### 4. Git Automation (`tools/git_ops.py`)
| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `install_git_hooks` | `repo_path: str = "."` | Install Git pre-commit hooks to auto-sync `.project_brain`. |

---

## ⚡ Performance Benchmarks

| Metric | v2.0.0 | v2.1.0 | Improvement |
| :--- | :--- | :--- | :--- |
| Path Validation (`security.py`) | 2.28 ms | 0.087 ms | **26.2× Faster** |
| Dependency Parsing (Cached `mtime`) | 450 ms | 0.12 ms | **3750× Faster** |
| Context Window Overhead (`DEV_MCP_PROFILE=code`) | ~12,500 tokens | ~4,200 tokens | **66.4% Reduction** |
| Context Window Overhead (`DEV_MCP_PROFILE=desktop`) | ~12,500 tokens | ~3,100 tokens | **75.2% Reduction** |
| Code Search (via Ripgrep vs Python scan) | 1,820 ms | 64 ms | **28.4× Faster** |

---

## 🔄 Migration & Compatibility

`dev-mcp` v2.1.0 is **100% backwards-compatible** with v2.0.0 and v1.x configurations.
- All existing `.project_brain` directories and `.project-context.json` formats remain valid.
- If `DEV_MCP_PROFILE` is omitted or set to `all`, all 84 tools are registered by default.
- Safety modes (`safe`, `trusted`, `lab`) continue to protect project boundaries.
