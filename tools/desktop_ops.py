"""
Desktop GUI automation and verification tools for dev-mcp via agent-desktop.

Bridges CLI, backend, and full-stack software development with native OS
accessibility tree automation, window management, and GUI verification.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from app import mcp


def _get_agent_desktop_bin() -> str:
    """Locate the agent-desktop binary."""
    found = shutil.which("agent-desktop")
    if found:
        return found
    fallback = Path("/home/dev/.npm-global/bin/agent-desktop")
    if fallback.is_file() and os.access(fallback, os.X_OK):
        return str(fallback)
    raise RuntimeError(
        "agent-desktop CLI not found. Install it using: npm install -g agent-desktop"
    )


def _run_ad_command(args: list[str], timeout: int = 30) -> dict | str:
    """Execute agent-desktop CLI command and parse JSON output."""
    binary = _get_agent_desktop_bin()
    cmd = [binary] + args
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy()
        )
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return stdout
        if stderr:
            return f"Error: {stderr}"
        return f"Command exited with code {res.returncode}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Execution error: {str(e)}"


@mcp.tool(
    name="desktop_status",
    description="Check desktop accessibility status, permissions, and supported surfaces.",
)
def desktop_status() -> str:
    """Check health, accessibility permissions, and capabilities of the desktop environment."""
    data = _run_ad_command(["status"])
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_list_apps",
    description="List all running GUI desktop applications.",
)
def desktop_list_apps() -> str:
    """Retrieve all running GUI applications on the desktop with process info."""
    data = _run_ad_command(["list-apps"])
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_list_windows",
    description="List all open windows with titles, dimensions, and window IDs.",
)
def desktop_list_windows(app: str = "") -> str:
    """List open windows, optionally filtered by application name."""
    args = ["list-windows"]
    if app:
        args.extend(["--app", app])
    data = _run_ad_command(args)
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_snapshot",
    description="Capture the accessibility tree of an application with actionable @refs.",
)
def desktop_snapshot(app: str, interactive_only: bool = True, compact: bool = True) -> str:
    """Capture structured accessibility JSON of an application with qualified element refs."""
    args = ["snapshot", "--app", app]
    if interactive_only:
        args.append("-i")
    if compact:
        args.append("--compact")
    data = _run_ad_command(args, timeout=20)
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_find",
    description="Search for UI elements matching a role, name, or text in an app.",
)
def desktop_find(app: str, role: str = "", name: str = "") -> str:
    """Find specific UI controls (e.g. role='button', name='Save') and return matching refs."""
    args = ["find", "--app", app]
    if role:
        args.extend(["--role", role])
    if name:
        args.extend(["--name", name])
    data = _run_ad_command(args)
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_click",
    description="Click an element using its qualified snapshot reference (@snapshot_id:eN).",
)
def desktop_click(ref_id: str, headed: bool = False) -> str:
    """Click a UI element via semantic accessibility press action or physical click."""
    args = ["click", ref_id]
    if headed:
        args.append("--headed")
    data = _run_ad_command(args)
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_type",
    description="Insert text into a text field target using its qualified ref.",
)
def desktop_type(ref_id: str, text: str, headed: bool = False) -> str:
    """Type text into an editable UI field."""
    args = ["type", ref_id, text]
    if headed:
        args.append("--headed")
    data = _run_ad_command(args)
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)


@mcp.tool(
    name="desktop_verify_element",
    description="Verify if a GUI element exists and assert its state (e.g. enabled, selected).",
)
def desktop_verify_element(app: str, role: str = "", name: str = "", expected_state: str = "") -> str:
    """Verify that a specific UI element exists in an application and check its state."""
    find_args = ["find", "--app", app]
    if role:
        find_args.extend(["--role", role])
    if name:
        find_args.extend(["--name", name])
        
    data = _run_ad_command(find_args)
    if not isinstance(data, dict) or not data.get("ok"):
        return f"Verification failed: Could not query application '{app}'."
        
    matches = data.get("data", {}).get("matches", [])
    if not matches:
        return f"❌ Verification Failed: No element matching role='{role}', name='{name}' found in app '{app}'."
        
    match = matches[0]
    states = match.get("states", [])
    
    if expected_state:
        if expected_state.lower() in [s.lower() for s in states]:
            return f"✅ Verification Passed: Found element '{name or role}' with state '{expected_state}'. Ref: {match.get('ref_id')}"
        else:
            return f"⚠️ Element Found with ref '{match.get('ref_id')}', but expected state '{expected_state}' was missing. Current states: {states}"
            
    return f"✅ Verification Passed: Found element '{match.get('name')}' (role: {match.get('role')}) with ref: {match.get('ref_id')}"


@mcp.tool(
    name="desktop_screenshot",
    description="Take a screenshot of an application window and save to target path.",
)
def desktop_screenshot(app: str, output_path: str) -> str:
    """Capture a PNG screenshot of a target application window."""
    args = ["screenshot", "--app", app, "--out", output_path]
    data = _run_ad_command(args)
    if isinstance(data, dict) and data.get("ok"):
        return f"Screenshot successfully saved to: {output_path}"
    return json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
