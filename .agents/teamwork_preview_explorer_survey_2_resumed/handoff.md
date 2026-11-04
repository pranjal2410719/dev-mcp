# MCP Tools, Security & Project Brain Audit Report

## 1. Observation

A comprehensive inspection of the `dev-mcp` repository (`/home/dev/Desktop/projects/mcp/dev-mcp`) was performed across all source files, tool modules, server entry points, security helpers, Project Brain subsystems, tests, and documentation.

### 1.1 Repository Architecture & Entry Points

- **`app.py`**:
  - Instantiates `FastMCP("dev-mcp", instructions=...)` (FastMCP 3.4.2 runtime).
  - Holds global state `_project_context: ProjectContext | None`.
  - `load_context(project_root: str | Path | None = None) -> ProjectContext`: resolves target root via `validate_path(project_root)` or `Path.cwd().resolve()`. Re-initializes `ProjectContext` whenever `_project_context._root != target_root`, ensuring workspace isolation without cross-project state leakage.
  - `set_context(ctx: ProjectContext) -> None`: updates the global context instance.
- **`server.py`**:
  - Registers all tools, prompts, and resources by importing 5 tool modules, 10 brain modules, 1 prompt module, and 1 resource module.
  - Implements dual-mode entrypoint:
    - **Non-interactive mode** (`not sys.stdin.isatty()`): calls `mcp.run()` directly over stdio pipes for MCP host clients (Antigravity, Cursor, Claude Desktop, Windsurf, Cline).
    - **Interactive mode** (`sys.stdin.isatty()`): starts `mcp.run()` in a daemon background thread (`name="mcp-server"`), renders a Rich ASCII banner, and spawns a `/dev/tty` raw keypress loop. Pressing `?`, `h`, or `/` invokes `cli.py` (the interactive guide) in a subprocess without interfering with the stdio channel; pressing `q` or `ESC` gracefully stops the server via `os._exit(0)`.
- **`pyproject.toml`**:
  - Version: `2.0.0`. Python requirement: `>=3.10`. Dependencies: `fastmcp>=2.0.0`, `readchar>=4.0.0`.
  - Scripts: `dev-mcp = "server:main"`, `dev-mcp-guide = "cli:main"`.

---

### 1.2 Exhaustive MCP Tool Inventory (71 Registered Tools)

All 71 tools registered on `FastMCP` were introspected programmatically via `mcp.list_tools()` and verified against function signatures and implementations:

#### Category A: File Operations (`tools/file_ops.py` — 8 tools)
1. **`read_file(path: str) -> str`**:
   - *Description*: Read full contents of a text file at given path.
   - *Error handling*: Validates path via `validate_path(path)`. Raises `FileNotFoundError` if not a file. Catches `UnicodeDecodeError` and returns `"[Binary file – {size} bytes]"`.
2. **`write_file(path: str, content: str) -> str`**:
   - *Description*: Write text content to file, creating parent directories recursively (`p.parent.mkdir(parents=True, exist_ok=True)`).
   - *Error handling*: Validates path via `validate_path(path)`. Returns `"Written {len(content)} characters to {p}"`.
3. **`edit_file(path: str, old_string: str, new_string: str) -> str`**:
   - *Description*: Targeted exact-string replacement within a file.
   - *Error handling*: Validates path via `validate_path(path)`. Raises `FileNotFoundError` if not file. Raises `ValueError` if `old_string not in content`. Returns `"Replaced {count} occurrence(s) in {p}"`.
4. **`delete_path(path: str) -> str`**:
   - *Description*: Delete a file or empty directory.
   - *Error handling*: Validates path. Raises `FileNotFoundError` if path does not exist. Raises `ValueError` if directory is not empty (advises using `delete_recursive`). Returns deletion status.
5. **`delete_recursive(path: str) -> str`**:
   - *Description*: Recursively delete a file or directory tree (`shutil.rmtree`).
   - *Error handling*: Validates path. Checks `safety_mode == "safe"`: raises `PermissionError("Action Blocked: 'delete_recursive' is forbidden under safety mode 'safe'...")`. Raises `FileNotFoundError` if path does not exist.
6. **`list_directory(path: str) -> str`**:
   - *Description*: List files and directories in path with sizes.
   - *Error handling*: Validates path. Raises `NotADirectoryError` if not a directory.
7. **`glob_files(pattern: str, base_path: str = ".") -> str`**:
   - *Description*: Search for files matching glob pattern recursively using `glob.glob(pattern, root_dir=base, recursive=True)`.
   - *Error handling*: Validates `base_path`. Returns `"No files matching '{pattern}' in {base}"` if empty.
8. **`create_directory(path: str) -> str`**:
   - *Description*: Create directory and missing parents (`mkdir -p`).
   - *Error handling*: Validates path. Returns `"Created directory: {p}"`.

#### Category B: Code Search (`tools/search.py` — 1 tool)
9. **`search_code(pattern: str, path: str = ".", glob_filter: str | None = None, max_results: int = 50) -> str`**:
   - *Description*: Ripgrep-based text/regex code search across files with pure-Python fallback.
   - *Error handling*: Validates path. Tries `shutil.which("rg")` with 30s timeout; on `subprocess.TimeoutExpired` returns `"Search timed out for '{pattern}'"`. Falls back to `os.walk` and `re.compile`; per-file read errors are caught and ignored.

#### Category C: Terminal Command Execution (`tools/terminal.py` — 1 tool)
10. **`run_command(command: str, timeout_seconds: int = 60, workdir: Optional[str] = None) -> str`**:
    - *Description*: Execute shell commands with timeout safety and command auditing.
    - *Error handling*:
      - Timeout clamped to `min(timeout_seconds, 300)`.
      - Working directory validated via `validate_path(workdir)`.
      - If `safety_mode != "lab"`:
        - Blocked patterns (`sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0`) raise `PermissionError`.
        - If `safety_mode == "safe"`, destructive commands (`rm -[a-zA-Z]*[rfRF]`, `rm --recursive`, `rm -d`, `git reset --hard`, `git clean -fd`) raise `PermissionError`.
        - Relative traversal (`".." in command"`) raises `PermissionError`.
        - Absolute paths outside `/bin`, `/usr/bin`, `/usr/lib`, `/lib`, `/etc/alternatives`, `/etc/ssl` that do not start with active project root raise `PermissionError`.
      - Subprocess execution: catches `subprocess.TimeoutExpired` -> returns `"[Timed out after {timeout}s]"`. Catches generic `Exception as e` -> returns `"[Error: {e}]"`. On success, returns `"[Exit code: {result.returncode}]\n{output}"`.

#### Category D: Git Operations (`tools/git_ops.py` — 7 tools)
11. **`git_status(repo_path: str = ".") -> str`**: Runs `git status` via `_git_cmd`.
12. **`git_diff(repo_path: str = ".", staged: bool = False) -> str`**: Runs `git diff` or `git diff --cached`.
13. **`git_log(repo_path: str = ".", max_count: int = 10) -> str`**: Runs `git log --max-count={max_count} --oneline --graph`.
14. **`git_branch(repo_path: str = ".") -> str`**: Runs `git branch`.
15. **`git_add(repo_path: str = ".", files: str = ".") -> str`**: Runs `git add <files>`.
16. **`git_commit(repo_path: str = ".", message: str = "update") -> str`**: Runs `git commit -m <message>`.
17. **`git_create_branch(repo_path: str = ".", branch_name: str = "") -> str`**: Runs `git checkout -b <branch_name>`. Returns `"Error: branch_name is required."` if empty.
*Common error handling for git tools*: `_git_cmd` validates `repo_path` via `validate_path`, catches `FileNotFoundError` (returns `"Git is not installed..."`), catches `subprocess.TimeoutExpired` (30s limit, returns `"[Git command timed out]"`), captures stdout and stderr.

#### Category E: Project Context Management (`tools/context_mgmt.py` — 11 tools)
18. **`init_context(path: str = ".") -> str`**: Scans project root for config files (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) and initializes/updates `.project-context.json`.
19. **`get_context(dot_path: str = "", path: str = ".") -> str`**: Retrieves full context JSON or specific value via dot notation.
20. **`update_context(dot_path: str, value: str, path: str = ".") -> str`**: Updates field at dot path.
21. **`add_to_context_list(dot_path: str, item: str, path: str = ".") -> str`**: Appends string or parsed JSON object to list field. Returns error if dot path is not a list.
22. **`add_key_file(file_path: str, purpose: str, details: str = "", root_path: str = ".") -> str`**: Adds file entry to `key_files` array.
23. **`add_task(task_id: str, description: str, status: str = "pending", branch: str = "", notes: str = "", path: str = ".") -> str`**: Adds active task to context `active_tasks`.
24. **`add_decision(decision: str, reason: str, alternatives: str = "", path: str = ".") -> str`**: Adds Architecture Decision Record (ADR) to `decisions`.
25. **`export_context_markdown(path: str = ".") -> str`**: Writes `.project-context.md` in root and returns preview.
26. **`remove_context_item(dot_path: str, index: int, path: str = ".") -> str`**: Removes element from list by index. Returns index error or list type error if invalid.
27. **`reset_context(path: str = ".") -> str`**: Resets context to defaults (`DEFAULT_CONTEXT`).
28. **`project_info(path: str = ".") -> str`**: Returns project language/framework detection, file count, directory count, git status, and context status.

#### Category F: PRD Management (`brain/prd_manager.py` — 4 tools)
29. **`get_prd(document: str = "PRD", path: str = ".") -> str`**: Reads specified PRD document (`PRD`, `VISION`, `SCOPE`, `REQUIREMENTS`) from `.project_brain/prd/<DOC>.md`.
30. **`update_prd(document: str, content: str, path: str = ".") -> str`**: Writes or overwrites document in `.project_brain/prd/<DOC>.md`.
31. **`summarize_prd(path: str = ".") -> str`**: Summarizes bullet requirements across all PRD documents.
32. **`compare_work_to_prd(path: str = ".") -> str`**: Compares active tasks against PRD requirements to evaluate alignment.

#### Category G: Phase & Milestone Management (`brain/phase_manager.py` — 7 tools)
33. **`get_current_phase(path: str = ".") -> str`**: Returns active development phase, status, and task count from `.project_brain/phases/phases.json`.
34. **`set_phase(phase_name: str, description: str = "", path: str = ".") -> str`**: Sets current active phase in `phases.json` and updates `ctx.project.current_phase`.
35. **`complete_phase(notes: str = "", path: str = ".") -> str`**: Marks current phase completed with timestamp and logs decision in context.
36. **`next_phase(phase_name: str, description: str = "", path: str = ".") -> str`**: Marks current phase complete and transitions to new phase.
37. **`list_phases(path: str = ".") -> str`**: Lists all phases sorted by start timestamp.
38. **`add_milestone(name: str, target_date: str = "", features: str = "", path: str = ".") -> str`**: Adds milestone to `.project_brain/phases/milestones.json`.
39. **`list_milestones(path: str = ".") -> str`**: Lists all milestones and completion statuses.

#### Category H: Todo & Task Backlog Engine (`brain/todo_engine.py` — 6 tools)
40. **`create_task(title: str, phase: str = "", priority: str = "medium", depends_on: str = "", description: str = "", path: str = ".") -> str`**: Generates structured `TASK-XXXX` ID, validates priority against `{"critical", "high", "medium", "low"}`, saves to `.project_brain/todos/active.json`, and mirrors to context `active_tasks`.
41. **`update_task(task_id: str, status: str = "", priority: str = "", title: str = "", path: str = ".") -> str`**: Updates status/priority/title. If status becomes `"completed"`, moves task from `active.json` to `completed.json` with completion timestamp, and synchronizes status with context. Returns `"Task {task_id} not found."` if missing.
42. **`complete_task(task_id: str, notes: str = "", path: str = ".") -> str`**: Helper wrapping `update_task(status="completed")`.
43. **`next_task(path: str = ".") -> str`**: Evaluates ready tasks whose dependencies are satisfied in `completed.json`, scoped to the current phase, sorted by priority.
44. **`blocked_tasks(path: str = ".") -> str`**: Lists tasks explicitly marked `"blocked"` or blocked by unmet dependency IDs.
45. **`list_tasks(phase: str = "", status: str = "", priority: str = "", path: str = ".") -> str`**: Lists active tasks filtered by phase, status, or priority, ordered by priority.

#### Category I: AI Handoff Engine (`brain/handoff_engine.py` — 3 tools)
46. **`generate_handoff(session_summary: str = "", known_issues: str = "", path: str = ".") -> str`**: Generates a comprehensive markdown handoff covering project state, active tasks (in progress, pending, blocked), completed tasks, session summary, known issues, and key files. Saves to `.project_brain/handoffs/<YYYY-MM-DD>.md`, logs entry to `session-log.json`, and writes `.project-context.md`.
47. **`get_last_handoff(path: str = ".") -> str`**: Loads the most recent handoff from `session-log.json`, falling back to latest `*.md` file in `handoffs/`, then `.project-context.md`.
48. **`list_handoffs(path: str = ".") -> str`**: Lists all historical handoffs with timestamps, phase, and task stats.

#### Category J: Orchestrator & Commit Flow (`brain/orchestrator.py` — 6 tools)
49. **`generate_project_brain(path: str = ".") -> str`**: Consolidates project name, description, current phase, active milestone, progress percentage, blocked tasks, active tasks, recent 3 git commits, and next recommended task into a unified JSON dashboard.
50. **`next_best_action(path: str = ".") -> str`**: Calculates next recommended task, extracts suggested file paths from task text using regex, and estimates time (1-2h for critical, 2-4h for high, 4-8h for medium, 8-16h for low).
51. **`start_session(path: str = ".") -> str`**: Prepares a markdown sprint start brief containing target task, previous handoff summary, and PRD excerpt.
52. **`end_session(session_summary: str, known_issues: str = "", path: str = ".") -> str`**: Closes development session, invokes `generate_handoff`, and outputs instructions to run `prepare_commit` and `commit_changes`.
53. **`prepare_commit(session_summary: str, path: str = ".") -> str`**: Audits `git status --porcelain` for modified and untracked files, infers Conventional Commit prefix (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`) and scope from modified files/summary, and outputs proposed commit message.
54. **`commit_changes(message: str, path: str = ".") -> str`**: Verifies Git repo, runs `git add .`, and executes `git commit -m <message>`. Returns commit stdout or error message.

#### Category K: Architecture Guardian (`brain/guardian.py` — 1 tool)
55. **`validate_architecture(path: str = ".") -> str`**: Scans codebase files (`.py`, `.ts`, `.tsx`, `.js`, etc.) against `forbidden_technologies` defined in context `architecture.rules` (defaults to `["redux", "firebase"]`). Checks imports with regex. Returns violation report with file paths, line numbers, and offending content.

#### Category L: Dependency Graph & Blast Radius (`brain/dependency.py` — 2 tools)
56. **`build_dependency_graph(path: str = ".") -> str`**: Parses JS/TS (`import ... from`, `require`) and Python (`import ...`, `from ... import`) imports to build directed adjacency graphs of dependencies (outgoing) and dependents (incoming).
57. **`impact_analysis(file_path: str, path: str = ".") -> str`**: Runs Breadth-First Search (BFS) over incoming dependents to calculate direct 1st-level affected files and recursive transitive downstream files (blast radius).

#### Category M: Reality Synchronization Engine (`brain/sync_engine.py` — 3 tools)
58. **`sync_workspace(path: str = ".") -> str`**: Scans physical git status (branch, modified/untracked/deleted files, last 5 commits) and matches them against active tasks using 4 heuristics: branch name matching, commit message matching, file name matching, and title keyword matching. Outputs confidence score and recommendation (`mark_complete` if confidence >= 80%, else `verify_work`).
59. **`verify_work(task_id: str, path: str = ".") -> str`**: Evaluates code reality against task requirements across 5 verification layers: target file existence, test file coverage, architectural compliance, git diff stats, and AI client review instructions. Outputs confidence percentage and verdict (`Mark Complete ✅` if >= 80%, `Requires Work 🛠️` if >= 50%, `Failed ❌` if < 50%).
60. **`project_dashboard(path: str = ".") -> str`**: Consolidates phase, milestone, plan progress %, health score (0-100 computed by penalizing blocked tasks [-5], architecture violations [-15], stale tasks [-3], and high blast-radius modified files [-5]), uncommitted files, recent commits, and handoff activity.

#### Category N: Requirements Traceability & Outcome Verification (`brain/requirements.py` — 3 tools)
61. **`extract_requirements(path: str = ".") -> str`**: Parses markdown PRD files in `.project_brain/prd/` for list items under requirement headings, extracts keywords, assigns `REQ-XXX` IDs, and saves to `.project_brain/prd/requirements.json`.
62. **`verify_requirements(feature_name: str = "", path: str = ".") -> str`**: Scans codebase files for requirement keywords, determines implementation status (marked implemented if >= 60% keyword match), calculates overall coverage percentage, and updates `requirements.json`.
63. **`verify_outcome(task_id: str, path: str = ".") -> str`**: Audits user experience outcome implementation: scans task files for UI form input capture (`form`, `input`, `onChange`, `TextField`), database persistence (`insert`, `save`, `supabase`, `axios`, `fetch`), and navigation routing (`router`, `navigate`, `push`, `Link`).

#### Category O: Project Onboarding, Readiness & Lifecycle (`brain/project_readiness.py` — 8 tools)
64. **`assess_project_readiness(path: str = ".") -> str`**: Scores workspace maturity from 0 to 100% across 8 weighted components: README (10%), PRD (20%), Architecture Rules (15%), Milestones (15%), Tasks (15%), Context Store (10%), Git (5%), Tests (10%). Assigns Maturity Level (Levels 0-5) and outputs next recommended command.
65. **`project_readiness_report(path: str = ".") -> str`**: Generates a detailed Markdown scoring matrix table, breakdown of missing components, and actionable onboarding steps.
66. **`bootstrap_project(path: str = ".") -> str`**: Greenfield initialization: creates `.project-context.json`, `.project_brain/config.yaml`, PRD template (`.project_brain/prd/PRD.md`), milestone stubs, and initial audit task.
67. **`adopt_existing_project(path: str = ".") -> str`**: Brownfield/legacy adoption: scans existing README, package managers, and directory structures, generates context, `.project_brain/config.yaml`, adopted PRD specification, Phase 1 milestone, and initial legacy audit tasks (`TASK-0001`, `TASK-0002`).
68. **`doctor(path: str = ".") -> str`**: Runs 7 health checks on MCP setup: FastMCP server running, context file existence and valid JSON, `.project_brain` directory, Git repository, PRD existence, `requirements.json` integrity, and active task backlog.
69. **`reset_project_brain(path: str = ".") -> str`**: Deletes `.project-context.json` and `.project_brain/` directory, clearing cached context in memory while leaving source code and git history untouched.
70. **`archive_project_brain(path: str = ".") -> str`**: Moves `.project-context.json` and `.project_brain/` to `.project_brain_archive/<YYYY-MM-DD_HH-MM-SS>/` before resetting or pivoting.
71. **`create_project_workspace(name: str, template: str = "blank", path: str = ".") -> str`**: Creates a new sibling project directory, initializes Git repository (`git init -b main`), calls `bootstrap_project`, configures template settings (`blank`, `nextjs`, or `python`), creates a workspace `README.md`, and runs initial commit.

---

### 1.3 MCP Resources & Prompts Inventory

#### Resources (`resources/definitions.py` — 2 resources)
1. **`project://context/json`**:
   - *MIME Type*: `application/json`
   - *Name*: Project Context (JSON)
   - *Description*: The full project context document as JSON.
   - *Implementation*: `json.dumps(get_context().data, indent=2)`
2. **`project://context/markdown`**:
   - *MIME Type*: `text/markdown`
   - *Name*: Project Context (Markdown)
   - *Description*: The full project context as a Markdown document for sharing.
   - *Implementation*: `get_context().to_markdown()`

#### Prompts (`prompts/definitions.py` — 4 prompts)
1. **`project-overview`**:
   - *Arguments*: `path: str = "."`
   - *Description*: A complete project overview prompt that injects the full project context for AI assistants.
2. **`code-review`**:
   - *Arguments*: `path: str = "."`
   - *Description*: Code review guidelines specific to this project's conventions and tech stack.
3. **`architectural-decision`**:
   - *Arguments*: none
   - *Description*: Template for recording an Architecture Decision Record (ADR).
4. **`feature-plan`**:
   - *Arguments*: none
   - *Description*: Template for planning a new feature with tasks, branch strategy, and milestones.

---

### 1.4 Security & Validation Model

#### 1. Path Resolution & Workspace Lock (`security.py`)
- **`get_allowed_dirs()`**: Resolves allowed directories: always includes `Path.cwd().resolve()`; parses colon-separated paths from environment variable `DEV_MCP_ALLOWED_DIRS`; and appends `Path.home()`.
- **`get_project_root_and_safety()`**: Obtains active project root from `app._project_context._root` (fallback: `Path.cwd().resolve()`). Reads `.project_brain/config.yaml` to extract `safety_mode` (default: `"safe"`).
- **`validate_path(path)`**:
  - Resolves path to absolute representation (`Path(path).resolve()`), neutralizing `..` path traversals and symbolic link escapes.
  - **Stack Inspection Bypass**: Inspects Python stack frames (`inspect.stack()`). If calling function is `bootstrap_project`, `create_project_workspace`, or `adopt_existing_project`, `is_bootstrap = True`.
  - **Workspace Lock Enforcement**: If `safety_mode in ("safe", "trusted")` and not `is_bootstrap`:
    - Checks `resolved.relative_to(root)` or `resolved == root`.
    - If outside root, raises `PermissionError(f"Workspace Lock Active: Access to '{resolved}' is blocked. Active safety mode '{safety_mode}' restricts all file operations to the project root '{root}'.")`.
  - **Fallback Allowlist**: If in `lab` mode or `is_bootstrap`, checks `resolved.relative_to(base)` across `get_allowed_dirs()`. If not in allowlist, raises `PermissionError`.

#### 2. Shell Command Sandboxing (`tools/terminal.py`)
- If `safety_mode != "lab"`:
  - Blocks dangerous system binaries: `sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0`.
  - Blocks relative path traversal: `".." in command` raises `PermissionError`.
  - Blocks external absolute paths: extracts paths matching `(/[a-zA-Z0-9_\-\.\+/]+)`. Any path not starting with `/bin`, `/usr/bin`, `/usr/lib`, `/lib`, `/etc/alternatives`, `/etc/ssl` must start with `root_str`, otherwise raises `PermissionError`.
- If `safety_mode == "safe"`:
  - Additionally blocks destructive deletions: `rm -rf`, `rm -r`, `rm -d`, `rm --recursive`.
  - Blocks destructive Git operations: `git reset --hard`, `git clean -fd`.
- Timeout: Clamped to `min(timeout_seconds, 300)`.
- Execution: `subprocess.run(..., shell=True, capture_output=True, text=True, timeout=timeout, cwd=str(cwd))`.

#### 3. Destructive Tool Sandboxing (`tools/file_ops.py`)
- `delete_recursive(path)` checks `safety_mode == "safe"` and raises `PermissionError`, directing the user to upgrade `safety_mode` to `trusted` or `lab`.

#### 4. Sensitive Data Protection (Critical Observation)
- **No secret scrubbing**: `tools/terminal.py` passes the entire ambient `os.environ` into `subprocess.run` without filtering.
- Command stdout and stderr are returned verbatim without token, credential, or password masking.
- `_mask_error_details` is a FastMCP server flag, but no custom data sanitizer or secret scrubber exists in `dev-mcp`.

---

### 1.5 Project Brain Subsystem Architecture

Project Brain is a file-based operating system for AI engineering that persists project state across discontinuous sessions.

#### Storage Layout:
```
<project-root>/
├── .project-context.json            # Central context store (tech stack, rules, key files, tasks, ADRs)
├── .project-context.md              # Auto-exported markdown mirror for AI ingestion
├── README.md                        # Standard human documentation
├── .project_brain/                  # Persistent Project Brain directory
│   ├── config.yaml                  # Workspace configuration (safety_mode, thresholds, auto_sync)
│   ├── prd/
│   │   ├── PRD.md                   # Product Requirements Document
│   │   ├── VISION.md                # Product Vision
│   │   ├── SCOPE.md                 # Scope & Boundaries
│   │   ├── REQUIREMENTS.md          # Additional requirements
│   │   └── requirements.json        # Extracted structured requirement tags (REQ-XXX)
│   ├── phases/
│   │   ├── phases.json              # Phase states, descriptions, task associations
│   │   └── milestones.json          # Milestone targets and feature lists
│   ├── todos/
│   │   ├── active.json              # Active tasks (TASK-XXXX) with phase, priority, deps
│   │   └── completed.json           # Completed task history with completion timestamps
│   └── handoffs/
│       ├── session-log.json         # Structured session history log
│       └── <YYYY-MM-DD>.md          # Daily AI session handoff briefs
└── .project_brain_archive/          # Safe migration/pivot archives (<timestamp>/)
```

#### Brain Lifecycle:
1. **Maturity Audit**: `assess_project_readiness` & `project_readiness_report` assess readiness score (0-100%).
2. **Onboarding**: `bootstrap_project` (fresh), `adopt_existing_project` (legacy), or `create_project_workspace` (isolated new workspace).
3. **Health Check**: `doctor` verifies 7 diagnostic layers.
4. **Session Startup**: `start_session` and `project_dashboard` output sprint brief and readiness state.
5. **Backlog & Sprints**: `create_task`, `update_task`, `next_task`, `set_phase`, `complete_phase`.
6. **Reality Synchronization**: `sync_workspace` compares git commits/diffs to tasks; `verify_work` validates implementation; `verify_requirements` checks keyword traceability; `verify_outcome` validates UX/DB flows.
7. **Architecture Protection**: `validate_architecture` catches forbidden imports; `impact_analysis` tracks blast radius.
8. **Session Wrapup**: `end_session` generates daily handoff markdown; `prepare_commit` drafts conventional commit; `commit_changes` commits.
9. **Archiving & Reset**: `archive_project_brain` preserves state before `reset_project_brain`.

---

### 1.6 Extension Points

1. **Adding New Tools**:
   - Import `mcp` from `app`.
   - Use `@mcp.tool(name=..., description=...)`.
   - Validate paths using `from security import validate_path`.
   - Ensure the module is imported in `server.py` so the decorator registers upon server startup.
2. **Adding New Resources**:
   - Import `mcp` from `app`.
   - Use `@mcp.resource(uri=..., name=..., description=..., mime_type=...)`.
   - Import module in `server.py`.
3. **Adding New Prompts**:
   - Import `mcp` from `app`.
   - Use `@mcp.prompt(name=..., description=...)`.
   - Import module in `server.py`.
4. **Schema Migrations / Hooks**:
   - `ProjectContext._ensure_fields()` performs recursive `deep_merge` on load to automatically migrate older context documents to new default schemas without data loss.

---

### 1.7 Discrepancies Identified

1. **Tool Count Discrepancy**:
   - `README.md` and `docs/user_manual.md` claim "Complete MCP Tool Reference (70 Tools)".
   - The actual registered tool count is **71 tools**. `create_project_workspace` is implemented and documented in the manual text, but omitted from the summary tool table in Section 6.A of `user_manual.md`.
2. **Server Comment Discrepancies**:
   - `server.py:15`: Claims "tools/ 10 existing generic tools" — there are actually 28 tools in `tools/`.
   - `server.py:51`: Claims "brain.todo_engine — 7 task engine tools" — there are actually 6 tools.
   - `server.py:53`: Claims "brain.orchestrator — 4 orchestration/session tools" — there are actually 6 tools (`prepare_commit` and `commit_changes` were added).
   - `server.py:58`: Claims "brain.project_readiness – 3 project onboarding tools" — there are actually 8 tools (`doctor`, `reset_project_brain`, `archive_project_brain`, `create_project_workspace`, etc.).
3. **Parameter Signature Discrepancies in Docs**:
   - In `docs/user_manual.md`, `update_task` parameters are documented as `task_id: str, title: str = "", description: str = "", phase: str = "", status: str = "", priority: str = "", depends_on: str = "", path: str = "."`. In actual code (`brain/todo_engine.py:143`), `update_task` only accepts `task_id: str, status: str = "", priority: str = "", title: str = "", path: str = "."`.
   - In `docs/user_manual.md`, parameter typing for `run_command(workdir)` and `search_code(glob_filter)` does not reflect `Optional[str]` / `str | None`.

---

## 2. Logic Chain

1. **From Code Inspection to Tool Inventory**:
   - Examining all files in `tools/` (5 files) and `brain/` (10 files) revealed 15 files declaring `@mcp.tool` decorators on `app.mcp`.
   - Querying FastMCP via `await mcp.list_tools()` yielded exactly 71 tools (28 in `tools/`, 43 in `brain/`).
   - Comparing this list with `README.md` and `docs/user_manual.md` identified that `create_project_workspace` in `brain/project_readiness.py` brought the count to 71, but the documentation headers and tables were written when there were 70 tools.

2. **From Security Code to Threat Model Assessment**:
   - Inspecting `security.py` showed that path jailing is enforced by `Path.resolve().relative_to(root)`.
   - Inspecting `inspect.stack()` in `validate_path()` revealed an intentional bypass mechanism for `bootstrap_project`, `create_project_workspace`, and `adopt_existing_project`.
   - Inspecting `tools/terminal.py` showed command pattern filtering (regex matching for dangerous commands, traversal `..`, and out-of-workspace absolute paths).
   - Inspecting `tools/terminal.py` and searching the codebase for secret masking revealed no redaction or sanitization of environment variables or command output, confirming that secret leakage prevention is currently unhandled at the tool layer.

3. **From Tests to Verification**:
   - Running `python -m unittest discover -s tests -v` confirmed 7 unit tests covering Workspace Lock, Safety Modes, Command Auditing, and Destructive File Operation Blocks pass.
   - Running `python -m unittest tests/validate_mcp_flow.py` confirmed the end-to-end onboarding, planning, and verification pipeline passes.

---

## 3. Caveats

1. **Subprocess Network Isolation**: `run_command` executes in the host shell environment without network namespaces or OS-level containerization (e.g. bubblewrap/docker). It relies purely on regex command blocklists and path checks.
2. **Terminal Shell Quoting**: Command path auditing in `tools/terminal.py` parses absolute paths using regex `(/[a-zA-Z0-9_\-\.\+/]+)`. Highly obfuscated paths or subshell expansions (`$(...)`) could evade simple string matching in `trusted` or `safe` mode if not blocked by pattern rules.
3. **Environment Variable Inheritance**: Subprocess commands inherit the full ambient environment of the host user running `dev-mcp`.

---

## 4. Conclusion

- `dev-mcp` v2.0.0 is a feature-complete, robust AI Engineering Operating System providing **71 MCP tools**, **2 MCP resources**, and **4 MCP prompts**.
- The security model successfully enforces workspace isolation and jailing via `validate_path()` and command execution pattern filters across three distinct safety tiers (`safe`, `trusted`, `lab`).
- Project Brain provides comprehensive project state persistence via `.project_brain/` and `.project-context.json`, supporting a 9-stage project lifecycle from readiness assessment to automated reality-synced git commits.
- Documentation updates are needed in `README.md`, `docs/user_manual.md`, and `server.py` to fix tool counts (70 -> 71), correct `update_task` parameter signatures, update server module comments, and explicitly document the absence of secret scrubbing.

---

## 5. Verification Method

To independently reproduce and verify all findings in this report, execute the following commands in `/home/dev/Desktop/projects/mcp/dev-mcp`:

1. **Verify Tool Count & Registration**:
   ```bash
   .venv/bin/python -c "
   import asyncio, server
   from app import mcp
   async def test():
       tools = await mcp.list_tools()
       prompts = await mcp.list_prompts()
       resources = await mcp.list_resources()
       print(f'Tools: {len(tools)}, Prompts: {len(prompts)}, Resources: {len(resources)}')
       assert len(tools) == 71, f'Expected 71, got {len(tools)}'
       assert len(prompts) == 4, f'Expected 4, got {len(prompts)}'
       assert len(resources) == 2, f'Expected 2, got {len(resources)}'
       print('Verification Passed: All counts match exactly.')
   asyncio.run(test())
   "
   ```

2. **Run Existing Test Suites**:
   ```bash
   # Run v2 feature unit tests (Workspace Lock, Safety Modes, Command Blocklist)
   .venv/bin/python -m unittest discover -s tests -v

   # Run end-to-end MCP workflow validation pipeline
   .venv/bin/python -m unittest tests/validate_mcp_flow.py
   ```

3. **Verify Tool Catalog Artifact**:
   Inspect the complete machine-readable tool catalog generated during this survey:
   `view_file /home/dev/Desktop/projects/mcp/dev-mcp/.agents/teamwork_preview_explorer_survey_2_resumed/tool_catalog.json`
