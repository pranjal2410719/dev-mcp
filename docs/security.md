# 🔒 Security Model & Workspace Lock

This document details the security constraints, safety modes, and jailing protections implemented in **`dev-mcp` v2.0.0**.

---

## 🛡️ 1. Workspace Lock (Jailing)

To prevent AI agents from wandering outside project roots and modifying critical operating system files, `dev-mcp` enforces a strict **Workspace Lock**.

By default, every path passed to a file operation (e.g., `read_file`, `write_file`, `edit_file`) or resolved by shell executions is checked:
- The path must be resolved to its absolute representation.
- It must be a child of the active project root directory.
- If it attempts to escape (via `..` traversal or accessing external absolute paths like `/etc` or `/home/user`), the server rejects it with a `PermissionError`.

*Note: The lock employs Python call-stack inspection (`inspect.stack()`) to detect onboarding operations (`bootstrap_project`, `create_project_workspace`, and `adopt_existing_project`). During these specific calls, the workspace lock is temporarily bypassed so that parent or sibling directories can be created and bootstrapped.*

---

## ⚙️ 2. Safety Modes

Configurations are parsed from `.project_brain/config.yaml`. The key parameter is `safety_mode`, which can be set to:

### A. `safe` (Default Mode)
This is the recommended mode for untrusted models or autonomous loops.
- **Workspace Lock**: Enabled. All file tool paths must resolve strictly within the active workspace root.
- **Blocked Shell Commands**: Heavy blocklist enabled. Prevents executing `sudo`, `dd`, `mkfs`, `reboot`, `shutdown`, `poweroff`, `init 0`, and recursive/destructive deletions like `rm -rf`, `rm -r`, `rm -d`, or `rm --recursive`.
- **Git Protections**: Blocks destructive git commands (`git reset --hard` and `git clean -fd`).
- **Destructive Tools**: Blocks recursive directory deletion tools (`delete_recursive`).

### B. `trusted`
Useful when the developer wants to grant the model the ability to reset git states or clean folders while keeping workspace path boundaries active.
- **Workspace Lock**: Enabled.
- **Blocked Shell Commands**: Dangerous system administration binaries (`sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0`) remain strictly blocked. Standard cleanup deletions (`rm -rf`) and Git resets are permitted within the workspace.
- **Destructive Tools**: Allowed (`delete_recursive` can be executed within the workspace).

### C. `lab`
Used inside isolated containers, virtual machines, or throwaway CI environments.
- **Workspace Lock**: Disabled. Resolves paths against the fallback allowlist: current working directory, directories specified in `DEV_MCP_ALLOWED_DIRS`, and `$HOME`.
- **Blocked Shell Commands**: Disabled. Allows arbitrary command execution without pattern blocklists.

---

## 🚫 3. Blocked Command Patterns

| Safety Mode | Blocked Command Patterns | Action Taken |
| :--- | :--- | :--- |
| `safe` & `trusted` | `sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0` | Returns `PermissionError` |
| `safe` | `rm -rf`, `rm -r`, `rm -d`, `rm --recursive`, `git reset --hard`, `git clean -fd` | Returns `PermissionError` |
| `safe` & `trusted` | Commands containing `..` relative path traversal | Returns `PermissionError` |
| `safe` & `trusted` | External absolute paths outside project root (except system directories: `/bin`, `/usr/bin`, `/usr/lib`, `/lib`, `/etc/alternatives`, `/etc/ssl`) | Returns `PermissionError` |

---

## 🛡️ 4. Sensitive Data & Process Environment

- **Environment Inheritance**: The `run_command` terminal tool inherits the ambient host process environment (`os.environ`) and returns stdout/stderr directly.
- **Secret Redaction**: `dev-mcp` does not perform automated token or API key scrubbing on shell outputs. Ensure production secrets and credentials are not placed in command arguments or unencrypted environment files.
