# 🚀 dev-mcp v2.2.0 Release Notes

**Release Date:** November 2026  
**Status:** Distribution & MCP Registry Release  
**Package Identity:** `braynix-dev-mcp` (PyPI) / `io.github.pranjal2410719/dev-mcp` (MCP Registry)  
**Total MCP Tools:** 91 Tools (18 Modules)  
**Transport:** Stdio (pure JSON-RPC)  

---

## 🌟 Executive Summary

`dev-mcp` version **2.2.0** delivers **zero-clone local distribution** and **official Model Context Protocol (MCP) Registry support**.

Rather than requiring developers to clone git repositories, configure local virtual environments, and manually link Python paths, `dev-mcp` can now be executed instantly with:

```bash
uvx --from braynix-dev-mcp dev-mcp
```

Or installed persistently across the developer's system:

```bash
uv tool install braynix-dev-mcp
```

---

## ⚡ Key Highlights of v2.2.0

1. **PyPI Local Distribution (`braynix-dev-mcp`)**:
   - Modernized build configuration using `setuptools>=68` and `wheel`.
   - Explicit runtime dependency pinning: `fastmcp>=3.4.2,<4`, `readchar>=4.0.0`, `rich>=13.7.0`.
   - Clean SPDX `MIT` license integration with zero deprecation build warnings.
   - Dual CLI entry points installed to system PATH:
     - `dev-mcp`: The primary MCP server entry point.
     - `dev-mcp-guide`: The interactive shortcut reference guide.

2. **Official MCP Registry Metadata (`server.json`)**:
   - Full alignment with official schema (`https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`).
   - Namespace registration: `io.github.pranjal2410719/dev-mcp`.
   - Package mapping: PyPI identifier `braynix-dev-mcp` with `uvx` runtime hint.
   - Ownership verification marker embedded in `README.md`.

3. **Pure Stdio JSON-RPC & Output Isolation**:
   - Guaranteed clean `stdout` for all pipe-connected MCP clients (Claude Desktop, Cursor, Windsurf, Antigravity CLI).
   - Zero terminal banners or escape sequences leaked into protocol streams.
   - All server diagnostics and non-protocol warnings routed strictly to `sys.stderr`.

4. **Desktop Automation Hardening**:
   - Dynamic user/system path discovery for `agent-desktop` binary across Linux, macOS, and Windows.
   - Graceful runtime fallback: if desktop automation CLI dependencies are missing, the server and remaining 75 tools continue functioning normally with helpful remediation messages.
   - Decoupled `tools.desktop_ops` from the `code` profile to ensure lightweight coding workflows.

5. **Automated Trusted Publishing (GitHub Actions)**:
   - Configured `.github/workflows/publish.yml` using short-lived OIDC tokens.
   - Isolated staging pipeline: Build ➔ TestPyPI Validation ➔ Production PyPI with environment gating.

---

## ⚙️ AI Client Configuration (v2.2.0)

### Cursor & Claude Desktop (`stdio`)

```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "braynix-dev-mcp",
        "dev-mcp"
      ],
      "env": {
        "DEV_MCP_PROFILE": "all"
      }
    }
  }
}
```

Or when installed permanently via `uv tool install braynix-dev-mcp`:

```json
{
  "mcpServers": {
    "dev-mcp": {
      "command": "dev-mcp",
      "env": {
        "DEV_MCP_PROFILE": "all"
      }
    }
  }
}
```

---

## 🔄 Upgrade & Compatibility

`dev-mcp` v2.2.0 is **100% backwards-compatible** with existing `.project_brain/` and `.project-context.json` workspace files created with v2.1.0 and v2.0.0.
