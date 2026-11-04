import re
import os
from pathlib import Path

project_root = Path("/home/dev/Desktop/projects/mcp/dev-mcp")

doc_files = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/architecture-v2.md",
    "docs/security.md",
    "docs/workspaces.md",
    "docs/user_manual.md",
    "docs/antigravity.md",
    "docs/architecture-eraser.md",
    "docs/open-design.md",
    "docs/release-notes-v2.0.0.md",
    "docs/releases/v2.0.0-summary.md",
]

# Load registered tools from mcp_catalog.json
import json
with open(project_root / ".agents/teamwork_preview_spec_miner_survey_1_resumed/mcp_catalog.json") as f:
    catalog = json.load(f)

valid_tools = set(catalog["tools"].keys())

print(f"Loaded {len(valid_tools)} valid MCP tools from catalog.\n")

# Regex patterns
link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
code_span_pattern = re.compile(r'`([a-zA-Z0-9_]+)`')

all_links = []
mentioned_tools_per_file = {}
headings_per_file = {}
file_contents = {}

for rel_path in doc_files:
    full_path = project_root / rel_path
    if not full_path.exists():
        print(f"MISSING FILE: {rel_path}")
        continue
    text = full_path.read_text(encoding="utf-8")
    file_contents[rel_path] = text
    
    # Extract headings and generate GitHub style anchor slugs
    headings = []
    for line in text.splitlines():
        if line.startswith("#"):
            h_text = line.lstrip("#").strip()
            # GitHub anchor slug: lowercase, replace spaces with hyphen, remove punctuation except hyphen
            # More accurately:
            slug = re.sub(r'[^\w\s-]', '', h_text.lower()).strip().replace(' ', '-')
            headings.append((h_text, slug))
    headings_per_file[rel_path] = headings

    # Extract links
    for match in link_pattern.finditer(text):
        label = match.group(1)
        target = match.group(2)
        # Skip external http/https/mailto
        all_links.append((rel_path, label, target))

    # Extract backtick mentions of possible tools
    code_spans = set(code_span_pattern.findall(text))
    # Filter to things that look like function names / snake_case or match tools
    tools_mentioned = {s for s in code_spans if s in valid_tools or ("_" in s and not s.isupper())}
    mentioned_tools_per_file[rel_path] = tools_mentioned

print("=== INTERNAL LINKS AUDIT ===")
broken_links = []
for source_file, label, target in all_links:
    if target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:"):
        continue
    
    # Split into file part and anchor part
    if "#" in target:
        target_path_part, anchor = target.split("#", 1)
    else:
        target_path_part, anchor = target, None

    source_dir = (project_root / source_file).parent
    
    if target_path_part == "":
        target_file_rel = source_file
        target_full_path = project_root / source_file
    else:
        target_full_path = (source_dir / target_path_part).resolve()
        try:
            target_file_rel = str(target_full_path.relative_to(project_root))
        except ValueError:
            target_file_rel = str(target_full_path)

    if not target_full_path.exists():
        broken_links.append((source_file, label, target, f"File does not exist: {target_full_path}"))
    else:
        if anchor:
            # Check anchor against headings in target file
            target_headings = headings_per_file.get(target_file_rel, [])
            target_slugs = [slug for _, slug in target_headings]
            # also check if anchor matches raw slug or if slug contains it
            if anchor not in target_slugs:
                broken_links.append((source_file, label, target, f"Anchor #{anchor} not found in {target_file_rel} (available slugs: {target_slugs[:5]}...)"))

print(f"Total internal links checked: {len([l for l in all_links if not (l[2].startswith('http') or l[2].startswith('mailto'))])}")
print(f"Broken links found: {len(broken_links)}")
for b in broken_links:
    print(f"  [{b[0]}] '{b[1]}' -> '{b[2]}': {b[3]}")

print("\n=== FABRICATED / HALLUCINATED TOOLS AUDIT ===")
all_mentioned_tools = set()
for f, tools in mentioned_tools_per_file.items():
    all_mentioned_tools.update(tools)

# Find suspected tool names mentioned in docs that are NOT in valid_tools
hallucinated = set()
for t in all_mentioned_tools:
    if t not in valid_tools:
        # filter out common words/code identifiers like python packages or config keys
        common_non_tools = {
            "fastmcp", "readchar", "rich", "pydantic", "pyproject_toml", "main",
            "cli_py", "app_py", "server_py", "setup_py", "uv", "pip", "pytest",
            "safety_mode", "allowed_directories", "workspace_root", "active_workspace",
            "project_brain", "tech_stack", "key_files", "active_tasks", "dot_path",
            "true", "false", "none", "json", "yaml", "md", "utf_8", "str", "dict",
            "list", "int", "bool", "float", "pathlib", "os_walk", "dir_path",
            "file_path", "test_v2_features", "validate_mcp_flow", "dev_mcp",
            "dev_mcp_guide", "mcp_server", "mcp_servers", "project_context",
            "session_summary", "known_issues", "feature_name", "repo_path",
            "branch_name", "task_id", "phase_name", "old_string", "new_string",
            "glob_filter", "max_results", "timeout_seconds", "workdir",
            "allowed_commands", "blocked_commands", "git_ops", "file_ops",
            "prd_manager", "phase_manager", "todo_engine", "handoff_engine",
            "sync_engine", "project_readiness", "architecture_v2", "user_manual",
            "auto_detect", "workspace_lock", "safe_mode", "trusted_mode", "lab_mode"
        }
        if t.lower() not in common_non_tools:
            hallucinated.add(t)

print(f"Suspected fabricated tool names mentioned in docs: {len(hallucinated)}")
for h in sorted(hallucinated):
    files_with_h = [f for f, t_set in mentioned_tools_per_file.items() if h in t_set]
    print(f"  ? {h} (in {files_with_h})")

print("\n=== MISSING TOOLS AUDIT ===")
# Valid tools NOT mentioned in any doc
unmentioned_tools = valid_tools - all_mentioned_tools
print(f"Tools in code completely missing from docs: {len(unmentioned_tools)}")
for u in sorted(unmentioned_tools):
    print(f"  - {u}")

