# 📋 Specification Miner Survey Handoff Report: dev-mcp Documentation Audit

**Agent:** Documentation Spec Miner (`teamwork_preview_spec_miner_survey_1_resumed`)  
**Parent Orchestrator:** `5c72539b-bc38-4a93-8dd0-4732b3ba6da0`  
**Working Directory:** `/home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_spec_miner_survey_1_resumed`  
**Repository Path:** `/home/dev/Desktop/projects/mcp/dev-mcp`  
**Date / Timestamp:** 2026-09-08T10:28:00Z  
**Status:** COMPLETE (Hard Handoff)  

---

## 1. Observation

### 1.1 Documentation Inventory
The repository contains 11 Markdown files and 1 binary PDF document:
1. `README.md` (463 lines, 28,002 bytes) — Primary repository README, overview, quickstart, client setup, onboarding flow, and tool reference table.
2. `CONTRIBUTING.md` (167 lines, 9,866 bytes) — Contribution guidelines, architectural mermaid diagram, layer breakdown, testing, and PR workflow.
3. `docs/architecture-v2.md` (79 lines, 3,578 bytes) — Architecture specification for v2.0.0, multi-agent topologies, sibling workspace layouts, and safety guardrails.
4. `docs/security.md` (52 lines, 2,679 bytes) — Security model, Workspace Lock jailing rules, and 3 safety modes (`safe`, `trusted`, `lab`).
5. `docs/workspaces.md` (50 lines, 2,302 bytes) — Multi-workspace sibling layout, Project Brain partitioning, and workspace creation flow.
6. `docs/user_manual.md` (408 lines, 23,385 bytes) — Comprehensive user manual, Antigravity CLI integration, detailed tool reference catalog, setup, and troubleshooting.
7. `docs/antigravity.md` (61 lines, 2,209 bytes) — Host client integration guide for Google DeepMind's Antigravity CLI (`agy`), process piping, and slash command reference.
8. `docs/architecture-eraser.md` (158 lines, 7,926 bytes, untracked in Git) — Eraser Cloud Architecture diagram DSL script, node definitions, and API render instructions.
9. `docs/open-design.md` (67 lines, 2,621 bytes) — Design-to-code integration guide, Open Design context metadata schema, and Figma pipeline concepts.
10. `docs/release-notes-v2.0.0.md` (52 lines, 3,925 bytes) — Official v2.0.0 release notes, changelog, and future roadmap.
11. `docs/releases/v2.0.0-summary.md` (50 lines, 2,080 bytes) — High-level release announcement summary for v2.0.0.
12. `docs/dev-mcp-user-manual.pdf` (binary, 35,627 bytes) — Legacy compiled PDF manual (unreferenced by any documentation).

### 1.2 Package Metadata & Entry Points (`pyproject.toml`)
- **Package Name:** `dev-mcp`
- **Current Version:** `2.0.0`
- **Requires Python:** `>=3.10`
- **Declared Dependencies:** `fastmcp>=2.0.0`, `readchar>=4.0.0`
- **Console Script Entry Points:**
  - `dev-mcp = "server:main"`
  - `dev-mcp-guide = "cli:main"`
- **Stale Packaging Artifact:** `dev_mcp.egg-info/PKG-INFO` records `Version: 0.1.0` and omits `readchar>=4.0.0` dependency.

### 1.3 Codebase Reality: Actual Registered MCP Capabilities
By programmatically inspecting the live FastMCP server instance (`app.mcp`), the actual capabilities registered in code are:
- **Total MCP Tools Registered:** **71 tools** (spread across 15 Python modules).
- **Total MCP Resources Registered:** **2 resources**:
  1. `project://context/json` (`Project Context (JSON)`)
  2. `project://context/markdown` (`Project Context (Markdown)`)
- **Total MCP Prompts Registered:** **4 prompts**:
  1. `project-overview`
  2. `code-review`
  3. `architectural-decision`
  4. `feature-plan`
- **CLI Commands (`cli.py`):**
  - Binary: `dev-mcp-guide` (supports options `--tab, -t [general|commands|shortcuts]`, `--no-interactive, -n`).
  - Contains an internal data list `COMMANDS` with **70 tools** (missing `create_project_workspace`).
- **Server Entrypoint (`server.py`):**
  - Binary: `dev-mcp` / `python server.py`.
  - Non-interactive mode (pipe/client connected): boots `mcp.run()`.
  - Interactive mode (TTY): displays ASCII banner, launches `mcp.run()` in background daemon thread, monitors `/dev/tty` for keypresses (`?`, `h`, `/` to launch `cli.py`, `esc`, `q` to quit).

---

## 2. Logic Chain

### 2.1 Tool Count and Missing Tool Analysis
- **Observation:** `README.md` lines 61, 248, 250, and `docs/user_manual.md` lines 133, 214 explicitly declare "70 MCP tools". `cli.py` docstring line 10 mentions "all 50+ MCP tools" while `COMMANDS` has 70 entries.
- **Observation:** Live introspection of `app.mcp` discovers exactly 71 `@mcp.tool` endpoints.
- **Cross-check:** The 71st tool is `create_project_workspace(name: str, template: str = "blank", path: str = ".")` defined in `brain/project_readiness.py:898`.
- **Inference:** When the v2.0.0 feature `create_project_workspace` was implemented (committed in `77eba32`), it was added to prose in `docs/workspaces.md` and `docs/release-notes-v2.0.0.md`, but developer documentation maintainers failed to add it to:
  1. `README.md` Section 1 tool reference table
  2. `docs/user_manual.md` Section 6.A tool reference table
  3. `cli.py` `COMMANDS` list
- **Conclusion:** Tool count across all documentation is off by 1 (70 claimed vs 71 implemented), and `create_project_workspace` is missing from all reference catalogs.

### 2.2 Parameter Signature Inaccuracies & Hallucinations
- **Observation:** `update_task` in `brain/todo_engine.py:143` has the exact signature:
  `def update_task(task_id: str, status: str = "", priority: str = "", title: str = "", path: str = ".") -> str:`
- **Observation:** In `README.md:283` and `docs/user_manual.md:247`, `update_task` is documented as:
  `task_id: str, title: str = "", description: str = "", phase: str = "", status: str = "", priority: str = "", depends_on: str = "", path: str = "."`
- **Inference:** The documentation fabricates three parameters for `update_task` (`description`, `phase`, `depends_on`). If an AI model or caller attempts to pass `update_task(task_id="TASK-1", description="new desc")`, FastMCP or Python raises a `TypeError` or silently fails.
- **Observation:** `list_tasks` in `brain/todo_engine.py:308` accepts `priority: str = ""`. The tables in `README.md:287` and `docs/user_manual.md:251` omit `priority`.

### 2.3 Fabrications and Stale Information in `docs/architecture-eraser.md`
- **Observation:** `docs/architecture-eraser.md` (untracked file) claims "73 tools across 15 modules".
- **Observation:** In the DSL body:
  - Lists `doctor` under `context_mgmt.py` (it is in `project_readiness.py`).
  - Lists `next_best_action` under BOTH `todo_engine.py` (line 43) and `orchestrator.py` (line 45), double-counting it.
  - Omits 5 real tools: `add_to_context_list`, `archive_project_brain`, `commit_changes`, `prepare_commit`, `reset_project_brain`.
  - Documents prompt `adr-template` instead of `architectural-decision`.
- **Inference:** `docs/architecture-eraser.md` was drafted from an unverified conceptual outline rather than the actual implementation.

### 2.4 Broken Machine-Specific Links (`file:///home/dev/...`)
- **Observation:** 42 links across `README.md`, `CONTRIBUTING.md`, `docs/user_manual.md`, `docs/release-notes-v2.0.0.md`, and `docs/releases/v2.0.0-summary.md` use the `file:///home/dev/Desktop/projects/mcp/dev-mcp/...` protocol.
- **Inference:** When developers viewed preview markdown files in a local editor or browser, local file paths were copied instead of repository-relative Markdown links.
- **Impact:** On GitHub or on any user's machine where the path is not `/home/dev/...`, every single one of these 42 links returns a 404 or fails to open.

### 2.5 Security Model Contradiction
- **Observation:** `README.md` lines 425-435 and `docs/user_manual.md` lines 383-394 state:
  "All file tools are sandboxed for security. Paths must resolve within directories in: 1. The server's current working directory. 2. DEV_MCP_ALLOWED_DIRS... 3. The user's home directory ($HOME)."
- **Observation:** `security.py:94` implements:
  `if safety_mode in ("safe", "trusted") and not is_bootstrap: resolved.relative_to(root)`
  This raises a `PermissionError("Workspace Lock Active: Access to '...' is blocked")` if any path is outside the active workspace root, regardless of `$HOME` or `DEV_MCP_ALLOWED_DIRS`.
- **Inference:** `README.md` and `docs/user_manual.md` still display the obsolete v1.0 security model, directly contradicting `docs/security.md` and `security.py`.

### 2.6 Configuration Drift (`config.yaml`)
- **Observation:** When `brain.project_readiness.bootstrap_project` generates `.project_brain/config.yaml`, it includes:
  `safety_mode: safe`
- **Observation:** The sample `config.yaml` in `README.md:414` and `docs/user_manual.md:372` completely omits `safety_mode`.

---

## 3. Caveats
1. **Host-Specific CLI Commands:** `docs/antigravity.md` references slash commands like `/goal`, `/schedule`, `/grill-me`, `/teamwork-preview`, and `/learn`. These are host client features of Google DeepMind's Antigravity CLI, not MCP server tools provided by `dev-mcp`. The docs must clearly state this distinction to avoid confusing users of Cursor, Claude Desktop, or Windsurf.
2. **External Script `./agy-auto`:** Mentioned in `docs/antigravity.md:49`. This script is not part of this git repository; it belongs to the host environment or external tooling.
3. **Editable Pip Install Metadata:** `dev_mcp.egg-info/PKG-INFO` is not git-tracked but generated locally during `pip install -e .`. Re-running `pip install -e .` with a modern build tool updates it to 2.0.0.
4. **Binary PDF Document:** `docs/dev-mcp-user-manual.pdf` is an existing binary file. Modifying it requires an external PDF generation tool (e.g. `pandoc` or `weasyprint`), which is outside the Markdown scope.

---

## 4. Conclusion & Definitive Catalog of Required Updates

### 4.1 Summary of Discrepancies by File and Severity

| File | Severity | Issue Summary | Specific Fix Required |
| :--- | :--- | :--- | :--- |
| **`README.md`** | 🔴 HIGH | Stale tool count: claims "70 tools" in 3 places (lines 61, 248, 250). | Update to "71 tools". |
| **`README.md`** | 🔴 HIGH | Missing tool: `create_project_workspace` omitted from tool reference table. | Add row for `create_project_workspace` under Section 1 (`brain/project_readiness.py`). |
| **`README.md`** | 🔴 HIGH | Hallucinated parameters in `update_task` (line 283): lists `description`, `phase`, `depends_on`. | Correct signature to `task_id: str, status: str = "", priority: str = "", title: str = "", path: str = "."`. |
| **`README.md`** | 🟡 MEDIUM | Missing parameter in `list_tasks` (line 287): omits `priority`. | Add `priority: str = ""` to documented signature. |
| **`README.md`** | 🔴 HIGH | 9 broken machine-specific `file:///` URLs (lines 61, 66-71, 444, 462). | Replace with relative paths (e.g. `docs/user_manual.md`, `CONTRIBUTING.md`). |
| **`README.md`** | 🔴 HIGH | Outdated security sandbox section (lines 425-435): claims `$HOME` is allowed. | Replace with v2.0.0 Workspace Lock & Safety Modes (`safe`, `trusted`, `lab`) documentation. |
| **`README.md`** | 🟡 MEDIUM | Stale `config.yaml` sample (lines 414-421): omits `safety_mode: safe`. | Add `safety_mode: safe` to the YAML example. |
| **`README.md`** | 🟡 MEDIUM | Hardcoded developer path `/home/dev/Desktop/projects/mcp/dev-mcp` across 8 examples. | Replace with generic portable paths (e.g. `/path/to/dev-mcp`). |
| **`CONTRIBUTING.md`** | 🔴 HIGH | 19 broken machine-specific `file:///` URLs (lines 56-59, 63-67, 71-80). | Replace all with relative markdown links (e.g. `server.py`, `tools/file_ops.py`). |
| **`CONTRIBUTING.md`** | 🟡 MEDIUM | Outdated security controller summary (line 59): mentions `$HOME`. | Update to reflect Workspace Lock and safety levels. |
| **`CONTRIBUTING.md`** | 🟡 MEDIUM | Test runner instructions (line 143): only mentions `validate_mcp_flow.py`. | Add `test_v2_features.py` and `python -m unittest` commands. |
| **`docs/user_manual.md`** | 🔴 HIGH | Stale tool count: claims "70 tools" in 2 places (lines 133, 214). | Update to "71 tools". |
| **`docs/user_manual.md`** | 🔴 HIGH | Missing tool: `create_project_workspace` missing from Section 6.A table. | Add row for `create_project_workspace` with arguments and description. |
| **`docs/user_manual.md`** | 🔴 HIGH | Hallucinated parameters in `update_task` (line 247). | Align signature with code (`task_id`, `status`, `priority`, `title`, `path`). |
| **`docs/user_manual.md`** | 🟡 MEDIUM | Missing parameter in `list_tasks` (line 251). | Add `priority: str = ""` to table signature. |
| **`docs/user_manual.md`** | 🔴 HIGH | 5 broken machine-specific `file:///` URLs (lines 165-168, 401). | Replace with relative paths (`security.md`, `../app.py`). |
| **`docs/user_manual.md`** | 🔴 HIGH | Contradictory security sandbox section (lines 383-394): claims `$HOME` is allowed. | Align Section 9 with Section 4.2 Workspace Lock specification. |
| **`docs/user_manual.md`** | 🟡 MEDIUM | Stale `config.yaml` sample (lines 372-379): omits `safety_mode: safe`. | Add `safety_mode: safe` to the YAML sample. |
| **`docs/user_manual.md`** | 🟡 MEDIUM | Hardcoded `/home/dev/...` paths across setup and client config snippets. | Replace with generic path placeholders. |
| **`cli.py`** | 🔴 HIGH | Missing tool in interactive guide: `create_project_workspace` omitted from `COMMANDS`. | Add `("Brain/Ready", "create_project_workspace", "Create isolated project workspace with git")` to `COMMANDS`. |
| **`cli.py`** | 🟡 MEDIUM | Docstring line 10 claims "all 50+ MCP tools". | Update docstring to reflect 71 MCP tools. |
| **`server.py`** | 🟡 MEDIUM | Docstring lines 15-25 describes stale module layout (claims 10 generic tools, omits 6 brain modules). | Update docstring module organization diagram to reflect all 15 modules. |
| **`docs/architecture-eraser.md`** | 🔴 HIGH | Untracked file with inaccurate tool counts (claims 73 tools, double-counts `next_best_action`, misplaces `doctor`, omits 5 tools, fabricates prompt name `adr-template`). | Fix DSL node definitions: 71 tools, correct module groupings, and prompt `architectural-decision`. Track file in git. |
| **`docs/antigravity.md`** | 🟡 MEDIUM | Hardcoded `/home/dev/...` absolute path in JSON config (lines 39-40). | Replace with generic path placeholder. |
| **`docs/antigravity.md`** | 🟢 LOW | Unclear distinction between host CLI slash commands and server tools. | Add explicit note that `/goal`, `/schedule`, `/grill-me` are host client features. |
| **`docs/release-notes-v2.0.0.md`** | 🔴 HIGH | 5 broken machine-specific `file:///` URLs (lines 33-37). | Replace with relative paths (`security.md`, `workspaces.md`, etc.). |
| **`docs/releases/v2.0.0-summary.md`**| 🔴 HIGH | 4 broken machine-specific `file:///` URLs (lines 46-49). | Replace with relative paths (`../release-notes-v2.0.0.md`, etc.). |

---

## 5. Verification Method

To independently verify these findings, execute the following commands in the workspace root:

1. **Verify Live Registered Tool / Resource / Prompt Counts:**
   ```bash
   .venv/bin/python -c '
   import sys, asyncio; sys.path.insert(0, ".")
   import server; from app import mcp
   tools = asyncio.run(mcp.list_tools())
   res = asyncio.run(mcp.list_resources())
   pm = asyncio.run(mcp.list_prompts())
   print(f"Tools: {len(tools)}, Resources: {len(res)}, Prompts: {len(pm)}")
   assert len(tools) == 71, f"Expected 71 tools, got {len(tools)}"
   assert len(res) == 2, f"Expected 2 resources, got {len(res)}"
   assert len(pm) == 4, f"Expected 4 prompts, got {len(pm)}"
   '
   ```

2. **Verify Tool Absence in CLI Guide:**
   ```bash
   .venv/bin/python -c '
   import cli
   cli_tools = {t[1] for t in cli.COMMANDS}
   assert "create_project_workspace" not in cli_tools, "create_project_workspace should be missing from cli.py"
   print(f"cli.py contains {len(cli_tools)} tools. Missing: create_project_workspace")
   '
   ```

3. **Verify Parameter Signature Mismatches (`update_task` & `list_tasks`):**
   ```bash
   .venv/bin/python -c '
   import inspect
   from brain.todo_engine import update_task, list_tasks
   print("update_task params:", list(inspect.signature(update_task).parameters.keys()))
   print("list_tasks params:", list(inspect.signature(list_tasks).parameters.keys()))
   '
   ```

4. **Verify Detection of all 42 Machine-Specific `file:///` URLs:**
   ```bash
   grep -rn "file:///home/dev" README.md CONTRIBUTING.md docs/
   ```

5. **Run Existing Test Suite:**
   ```bash
   .venv/bin/python -m unittest tests/test_v2_features.py tests/validate_mcp_flow.py
   ```
   (Expected result: Ran 8 tests in ~1.5s, OK).

---

## Features Discovered (All 71 Tools, 2 Resources, 4 Prompts & CLI)

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | File Ops | `read_file` | Read contents of file at given path | `path: str` | `str` (file contents) | `FileNotFoundError`, `PermissionError` (Workspace Lock) | `tools/file_ops.py:18` |
| 2 | File Ops | `write_file` | Write content to file, creating dirs if needed | `path: str`, `content: str` | `str` (confirmation) | `PermissionError` (Workspace Lock) | `tools/file_ops.py:35` |
| 3 | File Ops | `edit_file` | Replace exact string in file with new string | `path: str`, `old_string: str`, `new_string: str` | `str` (patch status) | `FileNotFoundError`, `ValueError` if old_string not found | `tools/file_ops.py:49` |
| 4 | File Ops | `delete_path` | Delete a file or empty directory | `path: str` | `str` (deletion status) | `FileNotFoundError`, `OSError` if directory not empty | `tools/file_ops.py:78` |
| 5 | File Ops | `delete_recursive` | Recursively delete file/directory tree | `path: str` | `str` (deletion status) | `PermissionError` in `safe` mode, `FileNotFoundError` | `tools/file_ops.py:103` |
| 6 | File Ops | `list_directory` | List files and directories with sizes | `path: str` | `str` (formatted directory listing) | `FileNotFoundError`, `NotADirectoryError` | `tools/file_ops.py:127` |
| 7 | File Ops | `glob_files` | Find files matching glob pattern | `pattern: str`, `base_path: str = "."` | `str` (matched file list) | `FileNotFoundError` if base_path missing | `tools/file_ops.py:146` |
| 8 | File Ops | `create_directory` | Create one or more directories (`mkdir -p`) | `path: str` | `str` (created path confirmation) | `PermissionError` (Workspace Lock) | `tools/file_ops.py:161` |
| 9 | Search | `search_code` | Ripgrep code pattern search with Python fallback | `pattern: str`, `path: str = "."`, `glob_filter: str = None`, `max_results: int = 50` | `str` (matched lines with file:line) | `FileNotFoundError` if path missing | `tools/search.py:19` |
| 10 | Terminal | `run_command` | Execute shell command with timeout and audit | `command: str`, `timeout_seconds: int = 60`, `workdir: str = None` | `str` (exit code + stdout + stderr) | `PermissionError` if dangerous/path escape, timeout status | `tools/terminal.py:17` |
| 11 | Git | `git_status` | Show working tree status | `repo_path: str = "."` | `str` (git status output) | Git error string | `tools/git_ops.py:49` |
| 12 | Git | `git_diff` | Show staged or unstaged diffs | `repo_path: str = "."`, `staged: bool = False` | `str` (git diff patch) | Git error string | `tools/git_ops.py:59` |
| 13 | Git | `git_log` | Show recent commit history | `repo_path: str = "."`, `max_count: int = 10` | `str` (commit history log) | Git error string | `tools/git_ops.py:71` |
| 14 | Git | `git_branch` | List local branches | `repo_path: str = "."` | `str` (branch list) | Git error string | `tools/git_ops.py:82` |
| 15 | Git | `git_add` | Stage file(s) for commit | `repo_path: str = "."`, `files: str = "."` | `str` (staging status) | Git error string | `tools/git_ops.py:92` |
| 16 | Git | `git_commit` | Commit staged changes with message | `repo_path: str = "."`, `message: str = "update"` | `str` (commit status) | Git error string | `tools/git_ops.py:103` |
| 17 | Git | `git_create_branch` | Create and switch to new branch | `repo_path: str = "."`, `branch_name: str = ""` | `str` (branch creation status) | Git error string | `tools/git_ops.py:114` |
| 18 | Context | `init_context` | Auto-detect stack and initialize context JSON | `path: str = "."` | `str` (detected stack summary) | `PermissionError` | `tools/context_mgmt.py:21` |
| 19 | Context | `get_context` | Get full context JSON or filter by dot path | `dot_path: str = ""`, `path: str = "."` | `str` (JSON string or scalar value) | Key error formatted in return string | `tools/context_mgmt.py:45` |
| 20 | Context | `update_context` | Update specific field using dot notation | `dot_path: str`, `value: str`, `path: str = "."` | `str` (confirmation) | Value conversion error string | `tools/context_mgmt.py:66` |
| 21 | Context | `add_to_context_list` | Append item to list field in context | `dot_path: str`, `item: str`, `path: str = "."` | `str` (confirmation) | `ValueError` if target is not a list | `tools/context_mgmt.py:84` |
| 22 | Context | `add_key_file` | Register key file with purpose in context | `file_path: str`, `purpose: str`, `details: str = ""`, `root_path: str = "."` | `str` (confirmation) | Context save error | `tools/context_mgmt.py:104` |
| 23 | Context | `add_task` | Add quick task to context active_tasks | `task_id: str`, `description: str`, `status: str = "pending"`, `branch: str = ""`, `notes: str = ""`, `path: str = "."` | `str` (confirmation) | Context save error | `tools/context_mgmt.py:121` |
| 24 | Context | `add_decision` | Log ADR in context decisions list | `decision: str`, `reason: str`, `alternatives: str = ""`, `path: str = "."` | `str` (confirmation) | Context save error | `tools/context_mgmt.py:142` |
| 25 | Context | `export_context_markdown` | Export context as Markdown document | `path: str = "."` | `str` (saved markdown status) | File write error | `tools/context_mgmt.py:163` |
| 26 | Context | `remove_context_item` | Remove item from context list by index | `dot_path: str`, `index: int`, `path: str = "."` | `str` (confirmation) | `IndexError`, `ValueError` | `tools/context_mgmt.py:180` |
| 27 | Context | `reset_context` | Reset context to default schema | `path: str = "."` | `str` (confirmation) | File write error | `tools/context_mgmt.py:193` |
| 28 | Context | `project_info` | Get summary of project environment | `path: str = "."` | `str` (formatted environment summary) | File read error | `tools/context_mgmt.py:204` |
| 29 | PRD | `get_prd` | Retrieve PRD markdown document content | `document: str = "PRD"`, `path: str = "."` | `str` (document content) | Returns error if doc not found | `brain/prd_manager.py:46` |
| 30 | PRD | `update_prd` | Create or update PRD markdown document | `document: str`, `content: str`, `path: str = "."` | `str` (confirmation) | File write error | `brain/prd_manager.py:65` |
| 31 | PRD | `summarize_prd` | Summarize key requirements into bullets | `path: str = "."` | `str` (bullet summary) | Warning if no PRD found | `brain/prd_manager.py:83` |
| 32 | PRD | `compare_work_to_prd` | Compare active tasks against PRD spec | `path: str = "."` | `str` (alignment report) | None (handles missing files) | `brain/prd_manager.py:111` |
| 33 | Phase | `get_current_phase` | Get active development phase and status | `path: str = "."` | `str` (current phase status) | Returns empty state notice | `brain/phase_manager.py:65` |
| 34 | Phase | `set_phase` | Set active development phase name | `phase_name: str`, `description: str = ""`, `path: str = "."` | `str` (confirmation) | File write error | `brain/phase_manager.py:96` |
| 35 | Phase | `complete_phase` | Mark active phase as complete | `notes: str = ""`, `path: str = "."` | `str` (completion summary) | Warning if no active phase | `brain/phase_manager.py:133` |
| 36 | Phase | `next_phase` | Complete active phase & advance to next | `phase_name: str`, `description: str = ""`, `path: str = "."` | `str` (advance confirmation) | File write error | `brain/phase_manager.py:169` |
| 37 | Phase | `list_phases` | List all defined phases and status | `path: str = "."` | `str` (formatted phases list) | Empty list notice | `brain/phase_manager.py:212` |
| 38 | Phase | `add_milestone` | Add release milestone with features | `name: str`, `target_date: str = ""`, `features: str = ""`, `path: str = "."` | `str` (confirmation) | File write error | `brain/phase_manager.py:242` |
| 39 | Phase | `list_milestones` | List all milestones and target dates | `path: str = "."` | `str` (formatted milestones list) | Empty list notice | `brain/phase_manager.py:264` |
| 40 | Todo | `create_task` | Create new structured task with deps | `title: str`, `phase: str = ""`, `priority: str = "medium"`, `depends_on: str = ""`, `description: str = ""`, `path: str = "."` | `str` (task ID created) | `ValueError` if phase/priority invalid | `brain/todo_engine.py:80` |
| 41 | Todo | `update_task` | Update task status, priority, or title | `task_id: str`, `status: str = ""`, `priority: str = ""`, `title: str = ""`, `path: str = "."` | `str` (update status) | Error string if task not found | `brain/todo_engine.py:139` |
| 42 | Todo | `complete_task` | Mark task as completed with notes | `task_id: str`, `notes: str = ""`, `path: str = "."` | `str` (completion status) | Error string if task not found | `brain/todo_engine.py:209` |
| 43 | Todo | `next_task` | Get highest priority unblocked task | `path: str = "."` | `str` (recommended task details) | Notice if no tasks ready | `brain/todo_engine.py:226` |
| 44 | Todo | `blocked_tasks` | List all tasks blocked by unmet deps | `path: str = "."` | `str` (blocked task list) | Notice if none blocked | `brain/todo_engine.py:275` |
| 45 | Todo | `list_tasks` | List tasks filtered by phase, status, priority | `phase: str = ""`, `status: str = ""`, `priority: str = ""`, `path: str = "."` | `str` (formatted tasks list) | Notice if no matching tasks | `brain/todo_engine.py:308` |
| 46 | Handoff | `generate_handoff` | Create AI session handoff document | `session_summary: str = ""`, `known_issues: str = ""`, `path: str = "."` | `str` (saved handoff path) | File write error | `brain/handoff_engine.py:57` |
| 47 | Handoff | `get_last_handoff` | Retrieve latest session handoff doc | `path: str = "."` | `str` (handoff content) | Notice if no handoff found | `brain/handoff_engine.py:175` |
| 48 | Handoff | `list_handoffs` | List all historical handoff documents | `path: str = "."` | `str` (list of handoffs) | Empty list notice | `brain/handoff_engine.py:215` |
| 49 | Orchestrator | `generate_project_brain` | Aggregate project status dashboard | `path: str = "."` | `str` (full project brain markdown) | Handles missing elements gracefully | `brain/orchestrator.py:88` |
| 50 | Orchestrator | `next_best_action` | Intelligently suggest next action/task | `path: str = "."` | `str` (action recommendation) | Fallback recommendation | `brain/orchestrator.py:187` |
| 51 | Orchestrator | `start_session` | Start sprint session, output Session Brief | `path: str = "."` | `str` (markdown session brief) | Handles missing docs | `brain/orchestrator.py:215` |
| 52 | Orchestrator | `end_session` | End sprint session & create handoff | `session_summary: str`, `known_issues: str = ""`, `path: str = "."` | `str` (session summary status) | File write error | `brain/orchestrator.py:271` |
| 53 | Orchestrator | `prepare_commit` | Suggest conventional git commit message | `session_summary: str`, `path: str = "."` | `str` (suggested commit message) | Notice if working tree clean | `brain/orchestrator.py:291` |
| 54 | Orchestrator | `commit_changes` | Commit changes with approved message | `message: str`, `path: str = "."` | `str` (git commit output) | Error if git commit fails | `brain/orchestrator.py:380` |
| 55 | Guardian | `validate_architecture` | Scan imports against architectural rules | `path: str = "."` | `str` (validation report) | Formatted violation alerts | `brain/guardian.py:46` |
| 56 | Dependency | `build_dependency_graph` | Parse module imports & construct graph | `path: str = "."` | `str` (JSON dependency graph) | Scan error | `brain/dependency.py:149` |
| 57 | Dependency | `impact_analysis` | Downstream blast radius analysis for file | `file_path: str`, `path: str = "."` | `str` (impact report with tiers) | `FileNotFoundError` if file missing | `brain/dependency.py:167` |
| 58 | Sync | `sync_workspace` | Match git commits/branch to todos | `path: str = "."` | `str` (sync reality report) | Git status errors | `brain/sync_engine.py:39` |
| 59 | Sync | `verify_work` | Deep task verification dossier | `task_id: str`, `path: str = "."` | `str` (verification dossier) | Error if task not found | `brain/sync_engine.py:218` |
| 60 | Sync | `project_dashboard` | Unified PM dashboard & health score | `path: str = "."` | `str` (full PM dashboard) | Handles missing files | `brain/sync_engine.py:369` |
| 61 | Requirements | `extract_requirements` | Parse PRD markdown into requirements.json | `path: str = "."` | `str` (extraction count status) | Error if PRD not found | `brain/requirements.py:41` |
| 62 | Requirements | `verify_requirements` | Scan codebase for requirement coverage | `feature_name: str = ""`, `path: str = "."` | `str` (traceability matrix) | Notice if requirements empty | `brain/requirements.py:118` |
| 63 | Requirements | `verify_outcome` | Audit UX/business goal outcome for task | `task_id: str`, `path: str = "."` | `str` (outcome audit report) | Error if task missing | `brain/requirements.py:224` |
| 64 | Readiness | `assess_project_readiness` | Score repo onboarding maturity (0-100%) | `path: str = "."` | `str` (readiness score & audit) | Handles empty repo | `brain/project_readiness.py:148` |
| 65 | Readiness | `project_readiness_report` | Generate Markdown readiness checklist | `path: str = "."` | `str` (markdown readiness report) | Handles empty repo | `brain/project_readiness.py:266` |
| 66 | Readiness | `bootstrap_project` | Scaffold fresh Project Brain & config | `path: str = "."` | `str` (list of created templates) | File write error | `brain/project_readiness.py:377` |
| 67 | Readiness | `adopt_existing_project` | Onboard legacy repo, draft PRD & tasks | `path: str = "."` | `str` (adoption summary) | File write error | `brain/project_readiness.py:514` |
| 68 | Readiness | `doctor` | 7-layer diagnostic health check | `path: str = "."` | `str` (diagnostic checklist) | Formatted issues list | `brain/project_readiness.py:688` |
| 69 | Readiness | `reset_project_brain` | Wipe Project Brain metadata (leaves code) | `path: str = "."` | `str` (reset confirmation) | PermissionError | `brain/project_readiness.py:811` |
| 70 | Readiness | `archive_project_brain` | Archive context to `.project_brain_archive/` | `path: str = "."` | `str` (archive confirmation) | File write error | `brain/project_readiness.py:852` |
| 71 | Readiness | `create_project_workspace` | Create isolated sibling workspace directory | `name: str`, `template: str = "blank"`, `path: str = "."` | `str` (created workspace status) | `ValueError` if dir exists & not empty | `brain/project_readiness.py:898` |
| 72 | Resource | `project://context/json` | Project Context JSON resource | URI lookup | `str` (raw JSON) | None | `resources/definitions.py:14` |
| 73 | Resource | `project://context/markdown` | Project Context Markdown resource | URI lookup | `str` (Markdown layout) | None | `resources/definitions.py:26` |
| 74 | Prompt | `project-overview` | Injects full project context for AI | `path: str = "."` | `str` (prompt text) | None | `prompts/definitions.py:13` |
| 75 | Prompt | `code-review` | Code review prompt with conventions | `path: str = "."` | `str` (prompt text) | None | `prompts/definitions.py:40` |
| 76 | Prompt | `architectural-decision` | Template for ADR documentation | None | `str` (prompt text) | None | `prompts/definitions.py:87` |
| 77 | Prompt | `feature-plan` | Feature planning blueprint template | None | `str` (prompt text) | None | `prompts/definitions.py:113` |
| 78 | CLI | `dev-mcp-guide` | Interactive terminal help & shortcut guide | `--tab, -t`, `--no-interactive, -n` | Rich terminal UI | Exit code 0 / 1 | `cli.py:444` |
| 79 | CLI | `dev-mcp` | FastMCP stdio server / TTY interactive shell | Standard stdio / TTY key reader | MCP stdio protocol / TTY | Clean process exit | `server.py:191` |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | `validate_path` | Absolute path `/home/dev/file.txt` when `safety_mode: safe` | Raises `PermissionError`: `Workspace Lock Active: Access to '/home/dev/file.txt' is blocked.` |
| 2 | `validate_path` | Relative path traversal `../../etc/passwd` | Raises `PermissionError` (escapes active project root). |
| 3 | `validate_path` | Target path during `create_project_workspace` or `bootstrap_project` | Allowed: Stack frame check detects onboarding functions and allows parent directory creation. |
| 4 | `validate_path` | Any path in `$HOME` or `DEV_MCP_ALLOWED_DIRS` when `safety_mode: lab` | Allowed: falls back to allowed directories allowlist. |
| 5 | `run_command` | `sudo apt-get update` under `safe` or `trusted` mode | Raises `PermissionError`: `Command matches dangerous pattern 'sudo' under safety mode.` |
| 6 | `run_command` | `rm -rf tmp/` under `safe` mode | Raises `PermissionError`: destructive deletion pattern blocked under `safe` mode. |
| 7 | `run_command` | `rm -rf tmp/` under `trusted` mode | Allowed: `rm -rf` permitted within workspace under `trusted` mode. |
| 8 | `run_command` | `cat ../sibling/file.txt` under `safe` or `trusted` mode | Raises `PermissionError`: `Relative path traversal '..' is forbidden`. |
| 9 | `run_command` | `cat /bin/ls` (standard system directory) | Allowed: path passes system directory whitelist (`/bin`, `/usr/bin`, etc.). |
| 10 | `run_command` | `cat /etc/shadow` | Raises `PermissionError`: path outside active workspace and not in system whitelist. |
| 11 | `delete_recursive` | Directory path under `safety_mode: safe` | Raises `PermissionError`: `Action Blocked: 'delete_recursive' is forbidden under safety mode 'safe'.` |
| 12 | `delete_recursive` | Directory path under `safety_mode: trusted` | Allowed: recursively removes target directory. |
| 13 | `create_project_workspace` | `name` of an existing directory containing files | Raises `ValueError`: `Directory '...' already exists and is not empty.` |
| 14 | `update_task` | Called with undocumented `description` or `phase` | Ignores extra kwargs if passed via python; FastMCP input validation will reject unrecognized parameters. |
| 15 | `load_context` | Invoked with different root than cached instance | Evicts stale cache and loads new workspace context, preventing cross-project state leakages. |
| 16 | `server.py` | Non-TTY stdin (piped MCP client connection) | Bypasses TTY banner and `/dev/tty` listener, calls `mcp.run()` directly with zero stdio interference. |
