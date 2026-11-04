# Project: dev-mcp Documentation Refresh & Codebase Alignment

## Architecture
- **Server Runtime**: FastMCP 3.4.2 application initialized in `app.py`.
- **Entry Points**:
  - `dev-mcp = "server:main"`: Dual-mode MCP server. Pipe mode runs stdio JSON-RPC for MCP clients (Antigravity, Cursor, Claude Desktop, Windsurf, Cline). TTY mode spawns background server thread with Rich ASCII banner and `/dev/tty` shortcut listener (`?`, `h`, `/` to launch interactive guide).
  - `dev-mcp-guide = "cli:main"`: Interactive Rich terminal shortcut & command reference guide (`--tab [general|commands|shortcuts]`, `--no-interactive`).
- **Workspace Model**:
  - Encapsulated by `ProjectContext` (`context.py`), backed by `.project-context.json` and `.project_brain/`.
  - Dynamic switching via `app.load_context(path)`.
  - Workspace Lock enforced via `security.validate_path(path)` ensuring all path operations resolve strictly within the active workspace root in `safe` and `trusted` modes.
  - Onboarding functions (`bootstrap_project`, `create_project_workspace`, `adopt_existing_project`) have stack-inspected bypasses to operate on new or sibling directories.
- **Security & Safety Tiers**:
  - `safe` (default): Workspace Lock active; shell blocklist (`sudo`, `mkfs`, `dd`, `shutdown`, `rm -rf`, `rm -r`, `rm -d`, `git reset --hard`, `git clean -fd`); traversal `..` blocked; external absolute paths blocked; `delete_recursive` blocked.
  - `trusted`: Workspace Lock active; system command blocklist; standard cleanup (`rm -rf`, `delete_recursive`) permitted.
  - `lab`: Workspace Lock disabled; fallback allowlist (`DEV_MCP_ALLOWED_DIRS`, CWD, `$HOME`).
  - *Note on Sensitive Data*: No secret/token scrubbing exists in `tools/terminal.py`; environment is inherited and returned verbatim.
- **Capabilities Ground Truth**:
  - Exactly **71 registered tools** (28 in `tools/`, 43 in `brain/`).
  - Exactly **2 registered resources** (`project://context/json`, `project://context/markdown`).
  - Exactly **4 registered prompts** (`project-overview`, `code-review`, `architectural-decision`, `feature-plan`).

## Feature Inventory
| # | Feature / Item | Description | Milestone | Source |
|---|----------------|-------------|-----------|--------|
| 1 | Tool Count Synchronization | Update all docs claiming 70 tools to 71 tools (including `create_project_workspace`) | M1 | Survey |
| 2 | `create_project_workspace` Catalog Entry | Add full parameter and return reference for `create_project_workspace` in README and user manual | M1 | Survey |
| 3 | `update_task` Signature Correction | Remove fabricated parameters (`description`, `phase`, `depends_on`); align with code signature | M1 | Survey |
| 4 | `list_tasks` Parameter Addition | Add missing `priority: str = ""` parameter to documentation tables | M1 | Survey |
| 5 | Broken Machine Links in Core Docs | Replace 33 machine-specific `file:///home/dev/...` links in README, CONTRIBUTING, and user_manual with relative paths | M1 | Survey |
| 6 | Security Sandbox Correction | Replace obsolete v1 sandbox ($HOME allowed) with v2 Workspace Lock and 3 safety modes in README and user manual | M1 | Survey |
| 7 | Config Sample Update | Add `safety_mode: safe` to sample `config.yaml` snippets in README and user manual | M1 | Survey |
| 8 | Portable Example Paths | Replace hardcoded `/home/dev/...` paths with generic placeholders (`/path/to/...`) | M1 | Survey |
| 9 | CONTRIBUTING.md Link & Test Updates | Fix links to source modules and add `test_v2_features.py` to test instructions | M1 | Survey |
| 10 | Specialized Docs Link Repair | Fix remaining 9 `file:///` URLs across release notes and summaries | M2 | Survey |
| 11 | `docs/architecture-eraser.md` Overhaul | Correct tool counts (71), module assignments (`doctor` in `project_readiness`), and prompt names (`architectural-decision`) | M2 | Survey |
| 12 | `docs/antigravity.md` Clarifications | Clarify distinction between host slash commands (`/goal`, `/schedule`) and server tools; sanitize hardcoded paths | M2 | Survey |
| 13 | Cross-doc Consistency & Versioning | Ensure all docs in `docs/` match 2.0.0 version and current architecture | M2 | Survey |
| 14 | `cli.py` Command Table Sync | Add `create_project_workspace` to `COMMANDS` list (bringing total to 71) and update docstring | M3 | Survey |
| 15 | `server.py` Comments Sync | Update stale tool count comments in module docstrings and registration blocks | M3 | Survey |
| 16 | Link Integrity Verification | Verify 100% internal Markdown links and anchors across all documentation files | M4 | Survey |
| 17 | Test Suite & Build Verification | Run `unittest` and `pytest` suites to ensure zero regressions | M4 | Survey |
| 18 | Packaging & Linting Check | Verify `pyproject.toml` version 2.0.0 and import cleanlines | M4 | Survey |
| 19 | Final Comprehensive Report | Generate detailed final report with git status, architecture summary, and READY TO PUSH verdict | M5 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Core Documentation Refresh | Refresh `README.md`, `CONTRIBUTING.md`, `docs/user_manual.md`: tool counts, signatures, security sandbox, sample configs, 33 link fixes | none | DONE |
| M2 | Specialized Docs & Architecture Refresh | Refresh `docs/security.md`, `docs/workspaces.md`, `docs/architecture-v2.md`, `docs/architecture-eraser.md`, `docs/open-design.md`, `docs/antigravity.md`, `docs/release-notes-v2.0.0.md`, `docs/releases/v2.0.0-summary.md` | none | DONE |
| M3 | CLI Guide & Code Alignment | Update `cli.py` `COMMANDS` table (add `create_project_workspace`, 71 tools) and `server.py` comment counts | none | IN_PROGRESS |
| M4 | Validation, Testing & Link Integrity | Run test suites, verify all internal Markdown links, check build & packaging | M1, M2, M3 | PLANNED |
| M5 | Final Report & Victory Readiness | Synthesize final report with git diff status, architecture, and READY TO PUSH verdict | M4 | PLANNED |

## Code Layout
- `README.md`: Primary repo documentation (Owned by M1 Worker)
- `CONTRIBUTING.md`: Developer contribution guide (Owned by M1 Worker)
- `docs/user_manual.md`: Complete user manual & tool reference (Owned by M1 Worker)
- `docs/security.md`: Security architecture & safety modes (Owned by M2 Worker)
- `docs/workspaces.md`: Multi-workspace design (Owned by M2 Worker)
- `docs/architecture-v2.md`: System architecture (Owned by M2 Worker)
- `docs/architecture-eraser.md`: Architecture diagram DSL (Owned by M2 Worker)
- `docs/antigravity.md`: Host client integration (Owned by M2 Worker)
- `docs/open-design.md`: Design context integration (Owned by M2 Worker)
- `docs/release-notes-v2.0.0.md`: Release notes (Owned by M2 Worker)
- `docs/releases/v2.0.0-summary.md`: Release summary (Owned by M2 Worker)
- `cli.py`: Interactive shortcut & command reference guide (Owned by M3 Worker)
- `server.py`: Server entrypoint and comments (Owned by M3 Worker)
