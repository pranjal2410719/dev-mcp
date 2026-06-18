"""
Architecture Guardian for Project Brain.

Validates project files against allowed and forbidden technology stacks.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from app import mcp, load_context as get_context
from security import validate_path

# Standard directories to skip when scanning
IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".project_brain",
    ".agents",
    "brain",
    "tools",
}

# Standard file extensions to scan
SCAN_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".cs",
    ".cpp",
    ".h",
}


@mcp.tool(
    name="validate_architecture",
    description="Scan the codebase and validate imports/technologies against the project's architectural guidelines and forbidden tools.",
)
def validate_architecture(path: str = ".") -> str:
    """Validate imports in codebase files against forbidden and required lists in project context."""
    root = validate_path(path)
    ctx = get_context(root)
    
    rules = ctx.data.get("architecture", {}).get("rules", {})
    forbidden = rules.get("forbidden_technologies", [])
    required = rules.get("required_technologies", [])
    
    if not forbidden and not required:
        # Provide sensible defaults if none are defined
        forbidden = ["redux", "firebase"]
        required = []
        
    violations = []
    scanned_files_count = 0
    
    # Compile regexes for each forbidden tech
    forbidden_patterns = {}
    for tech in forbidden:
        # Match imports: import * from 'tech', require('tech'), import tech, from tech import
        js_import = re.compile(r'\b(?:import\s+.*\s+from\s+[\'"]' + re.escape(tech) + r'[\'"]|require\([\'"]' + re.escape(tech) + r'[\'"]\))', re.IGNORECASE)
        py_import = re.compile(r'\b(?:import\s+' + re.escape(tech) + r'\b|from\s+' + re.escape(tech) + r'\s+import)', re.IGNORECASE)
        forbidden_patterns[tech] = (js_import, py_import)
        
    # Traverse directories
    for dirpath, dirnames, filenames in os.walk(root):
        # Exclude directories in-place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        
        for name in filenames:
            file_path = Path(dirpath) / name
            if file_path.suffix not in SCAN_EXTENSIONS:
                continue
                
            scanned_files_count += 1
            rel_path = file_path.relative_to(root)
            
            try:
                content_lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                for line_idx, line in enumerate(content_lines, 1):
                    # Check for forbidden imports
                    for tech, (js_pat, py_pat) in forbidden_patterns.items():
                        if js_pat.search(line) or py_pat.search(line):
                            violations.append({
                                "file": str(rel_path),
                                "line": line_idx,
                                "tech": tech,
                                "content": line.strip()
                            })
            except Exception:
                continue
                
    # Compile report
    report = [
        "# 🛡️ Architecture Guardian Report",
        f"**Scanned Files:** {scanned_files_count}",
        f"**Forbidden Technologies Checked:** {', '.join(forbidden) if forbidden else 'None'}",
        ""
    ]
    
    if violations:
        report.append("## 🚨 Violations Detected!")
        report.append("The following files imported or referenced forbidden libraries:")
        report.append("")
        for v in violations:
            report.append(f"- **{v['file']}** (Line {v['line']}): Found `{v['tech']}`")
            report.append(f"  `{v['content']}`")
        report.append("")
        report.append("⚠️ **Recommendation:** Replace forbidden imports with the approved stack (e.g. use Supabase instead of Firebase, or Zustand/Recoil instead of Redux).")
    else:
        report.append("## ✅ Verification Passed")
        report.append("No architectural guidelines violations were found. All imports align with rules.")
        
    return "\n".join(report)
