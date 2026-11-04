import json
import re
import sys
from pathlib import Path

project_root = Path("/home/dev/Desktop/projects/mcp/dev-mcp")
sys.path.insert(0, str(project_root))

with open(project_root / ".agents/teamwork_preview_spec_miner_survey_1_resumed/mcp_catalog.json") as f:
    catalog = json.load(f)

actual_tools = catalog["tools"]

# CLI commands
import cli
cli_tool_names = set(t[1] for t in cli.COMMANDS)

# Architecture eraser tools
eraser_content = (project_root / "docs/architecture-eraser.md").read_text(encoding="utf-8")
eraser_tool_mentions = set()
for t in actual_tools.keys():
    if t in eraser_content:
        eraser_tool_mentions.add(t)

# README tools
readme_content = (project_root / "README.md").read_text(encoding="utf-8")
readme_matches = re.findall(r'\|\s*`([a-zA-Z0-9_]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|', readme_content)
readme_table_tools = {m[0]: (m[1].strip(), m[2].strip()) for m in readme_matches}

# User manual tools
manual_content = (project_root / "docs/user_manual.md").read_text(encoding="utf-8")
manual_matches = re.findall(r'\|\s*`([a-zA-Z0-9_]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|', manual_content)
manual_table_tools = {m[0]: (m[1].strip(), m[2].strip()) for m in manual_matches}

print("=== TOOL COMPARISON SUMMARY ===")
print(f"Total tools in code: {len(actual_tools)}")
print(f"Total tools in cli.py: {len(cli_tool_names)}")
print(f"Total tools in README.md table: {len(readme_table_tools)}")
print(f"Total tools in docs/user_manual.md table: {len(manual_table_tools)}")
print(f"Total tools mentioned in docs/architecture-eraser.md: {len(eraser_tool_mentions)}")

print("\n--- Missing from cli.py ---")
for t in sorted(actual_tools.keys() - cli_tool_names):
    print(f"  {t}")

print("\n--- Missing from README.md table ---")
for t in sorted(actual_tools.keys() - set(readme_table_tools.keys())):
    print(f"  {t}")

print("\n--- Missing from docs/user_manual.md table ---")
for t in sorted(actual_tools.keys() - set(manual_table_tools.keys())):
    print(f"  {t}")

print("\n--- Missing from docs/architecture-eraser.md ---")
for t in sorted(actual_tools.keys() - eraser_tool_mentions):
    print(f"  {t}")

