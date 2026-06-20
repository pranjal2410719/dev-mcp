# 🔒 Security Model & Workspace Lock

This document details the security constraints, safety modes, and jailing protections implemented in **`dev-mcp` v2.0.0**.

---

## 🛡️ 1. Workspace Lock (Jailing)

To prevent AI agents from wandering outside project roots and modifying critical operating system files, `dev-mcp` enforces a strict **Workspace Lock**.

By default, every path passed to a file operation (e.g., `read_file`, `write_file`, `edit_file`) or resolved by shell executions is checked:
- The path must be resolved to its absolute representation.
- It must be a child of the active project root directory.
- If it attempts to escape (via `..` traversal or writing to absolute directories like `/home/dev`), the server rejects it with a `PermissionError`.

*Note: The lock is temporarily bypassed during onboarding operations (like `create_project_workspace` or `bootstrap_project`) to allow parent directories setup.*

---

## ⚙️ 2. Safety Modes

Configurations are parsed from `.project_brain/config.yaml`. The key parameter is `safety_mode`, which can be set to:

### A. `safe` (Default Mode)
This is the recommended mode for untrusted models or autonomous loops.
- **Workspace Lock**: Enabled.
- **Blocked Shell Commands**: Heavy block list enabled. Prevents executing `sudo`, `dd`, `mkfs`, `reboot`, `shutdown`, and standard recursive removals like `rm -rf` or `rm -d`.
- **Git Protections**: Blocks destructive git commands (such as `git reset --hard` and `git clean -fd`).
- **Destructive Tools**: Blocks recursive deletion tools (`delete_recursive`).

### B. `trusted`
Useful when the developer wants to grant the model the ability to reset git states or clean folders while keeping path limits active.
- **Workspace Lock**: Enabled.
- **Blocked Shell Commands**: Destructive system actions (like `sudo` or `reboot`) are blocked. Standard deletions and git checkouts are allowed.
- **Destructive Tools**: Allowed.

### C. `lab`
Used inside sandbox containers or throwaway virtual environments.
- **Workspace Lock**: Disabled.
- **Blocked Shell Commands**: Disabled. Allows all arbitrary actions.

---

## 🚫 3. Blocked Command Patterns

| Safety Mode | Blocked Command Patterns | Action Taken |
| :--- | :--- | :--- |
| `safe` & `trusted` | `sudo`, `mkfs`, `dd`, `shutdown`, `reboot`, `poweroff`, `init 0` | Returns `PermissionError` |
| `safe` | `rm -rf`, `rm -r`, `rm -f`, `rm -d`, `git reset --hard`, `git clean -fd` | Returns `PermissionError` |
| `safe` & `trusted` | Commands containing `..` path traversal | Returns `PermissionError` |
| `safe` & `trusted` | Absolute paths not starting with active project root | Returns `PermissionError` |
