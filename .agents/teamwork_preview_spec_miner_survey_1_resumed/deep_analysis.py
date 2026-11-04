import re
import os
import json
import inspect
from pathlib import Path

project_root = Path("/home/dev/Desktop/projects/mcp/dev-mcp")

with open(project_root / ".agents/teamwork_preview_spec_miner_survey_1_resumed/mcp_catalog.json") as f:
    catalog = json.load(f)

actual_tools = catalog["tools"]
actual_tool_names = set(actual_tools.keys())

# 1. Check tool signatures in README.md and user_manual.md
def extract_table_tools(filepath):
    content = (project_root / filepath).read_text(encoding="utf-8")
    # Table rows: | `tool_name` | `params` | Description |
    rows = re.findall(r'\|\s*`([a-zA-Z0-9_]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|', content)
    tools = {}
    for name, params, desc in rows:
        tools[name] = {"params": params.strip(), "desc": desc.strip()}
    return tools

readme_tools = extract_table_tools("README.md")
manual_tools = extract_table_tools("docs/user_manual.md")

print(f"README table tool count: {len(readme_tools)}")
print(f"user_manual table tool count: {len(manual_tools)}")
print(f"Actual tools in code: {len(actual_tool_names)}")

# Missing from README
missing_readme = sorted(list(actual_tool_names - set(readme_tools.keys())))
print(f"\nMissing from README table ({len(missing_readme)}): {missing_readme}")

# Missing from user_manual
missing_manual = sorted(list(actual_tool_names - set(manual_tools.keys())))
print(f"Missing from user_manual table ({len(missing_manual)}): {missing_manual}")

# Extra in README
extra_readme = sorted(list(set(readme_tools.keys()) - actual_tool_names))
print(f"Extra/non-existent in README table ({len(extra_readme)}): {extra_readme}")

# Extra in user_manual
extra_manual = sorted(list(set(manual_tools.keys()) - actual_tool_names))
print(f"Extra/non-existent in user_manual table ({len(extra_manual)}): {extra_manual}")

# Parameter differences
print("\n=== PARAMETER SIGNATURE CHECK ===")
for t_name in sorted(readme_tools.keys()):
    if t_name in actual_tools:
        doc_params = readme_tools[t_name]["params"]
        code_params = actual_tools[t_name]["parameters"]
        code_param_names = list(code_params.keys())
        
        # Check if parameter names match
        for p in code_param_names:
            if p not in doc_params:
                print(f"Parameter mismatch for {t_name}: code has '{p}' with required={code_params[p]['required']}, not clearly in doc '{doc_params}'")

# Check version strings across all files
print("\n=== VERSION REFERENCES CHECK ===")
version_regex = re.compile(r'\b(v?\d+\.\d+\.\d+)\b')
files_to_check = [
    "pyproject.toml",
    "README.md",
    "CONTRIBUTING.md",
    "cli.py",
    "server.py",
    "app.py",
    "context.py",
    "security.py",
    "docs/architecture-v2.md",
    "docs/architecture-eraser.md",
    "docs/security.md",
    "docs/workspaces.md",
    "docs/user_manual.md",
    "docs/antigravity.md",
    "docs/open-design.md",
    "docs/release-notes-v2.0.0.md",
    "docs/releases/v2.0.0-summary.md",
]

for f in files_to_check:
    fp = project_root / f
    if fp.exists():
        content = fp.read_text(encoding="utf-8")
        matches = set(version_regex.findall(content))
        print(f"{f}: {sorted(list(matches))}")

# Check all file:// links
print("\n=== FILE:// PROTOCOL LINKS CHECK ===")
file_proto_regex = re.compile(r'\[([^\]]+)\]\((file:///[^)]+)\)')
for f in files_to_check:
    fp = project_root / f
    if fp.exists():
        content = fp.read_text(encoding="utf-8")
        for match in file_proto_regex.finditer(content):
            label = match.group(1)
            url = match.group(2)
            print(f"{f}: [{label}]({url})")

# Check hardcoded paths like /home/dev/
print("\n=== HARDCODED /home/dev/ PATHS IN DOCS ===")
for f in files_to_check:
    fp = project_root / f
    if fp.exists() and f.endswith(".md"):
        content = fp.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            if "/home/dev" in line:
                print(f"{f}:{idx}: {line.strip()}")

