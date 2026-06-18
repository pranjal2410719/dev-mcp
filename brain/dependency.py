"""
Dependency Graph and Impact Analysis engine for Project Brain.

Scans imports across codebase to map connections and analyze edit impact.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
import json
from app import mcp
from security import validate_path

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
}


def _resolve_js_ts_import(source_file: Path, import_str: str, root: Path) -> Path | None:
    """Resolve JS/TS relative imports to actual file paths."""
    if not import_str.startswith("."):
        return None  # External package
        
    dirpath = source_file.parent
    base_target = (dirpath / import_str).resolve()
    
    # Try direct file resolutions
    for ext in (".ts", ".tsx", ".js", ".jsx", ".json"):
        candidate = base_target.with_suffix(ext)
        if candidate.is_file():
            return candidate.relative_to(root)
            
    # Try directory resolutions (index files)
    if base_target.is_dir():
        for index_name in ("index.ts", "index.tsx", "index.js", "index.jsx"):
            candidate = base_target / index_name
            if candidate.is_file():
                return candidate.relative_to(root)
                
    return None


def _resolve_python_import(source_file: Path, import_str: str, root: Path) -> Path | None:
    """Resolve Python absolute or relative imports to file paths."""
    # Handle relative imports e.g., 'from .app import mcp' or 'from ..utils import X'
    if import_str.startswith("."):
        dots_count = len(import_str) - len(import_str.lstrip("."))
        target_parts = import_str.lstrip(".").split(".")
        
        dirpath = source_file.parent
        for _ in range(dots_count - 1):
            dirpath = dirpath.parent
            
        base_target = dirpath
        if target_parts and target_parts[0]:
            base_target = base_target.joinpath(*target_parts)
            
        candidate = base_target.with_suffix(".py")
        if candidate.is_file():
            return candidate.relative_to(root)
            
        # Check folder __init__.py
        candidate_init = base_target / "__init__.py"
        if candidate_init.is_file():
            return candidate_init.relative_to(root)
            
    # Handle absolute imports relative to project root e.g., 'brain.todo_engine'
    parts = import_str.split(".")
    candidate = root.joinpath(*parts).with_suffix(".py")
    if candidate.is_file():
        return candidate.relative_to(root)
        
    candidate_init = root.joinpath(*parts) / "__init__.py"
    if candidate_init.is_file():
        return candidate_init.relative_to(root)
        
    return None


def _get_graph(root: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Scan root files and build adjacency lists: dependencies (outgoing) and dependents (incoming)."""
    dependencies: dict[str, list[str]] = {}
    dependents: dict[str, list[str]] = {}
    
    js_import_re = re.compile(r'\b(?:import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))')
    py_import_re = re.compile(r'\b(?:import\s+([\w\.]+)|from\s+([\w\.]+)\s+import)')
    
    # Pre-populate dictionaries for all scanned files
    all_files = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        
        for name in filenames:
            file_path = Path(dirpath) / name
            suffix = file_path.suffix
            if suffix not in (".py", ".ts", ".tsx", ".js", ".jsx"):
                continue
            rel = str(file_path.relative_to(root))
            all_files.append((file_path, rel, suffix))
            dependencies[rel] = []
            dependents[rel] = []
            
    # Parse each file
    for file_path, rel, suffix in all_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
            
        targets = []
        
        if suffix in (".js", ".jsx", ".ts", ".tsx"):
            for match in js_import_re.finditer(content):
                imp = match.group(1) or match.group(2)
                if imp:
                    resolved = _resolve_js_ts_import(file_path, imp, root)
                    if resolved:
                        targets.append(str(resolved))
                        
        elif suffix == ".py":
            for match in py_import_re.finditer(content):
                imp = match.group(1) or match.group(2)
                if imp:
                    resolved = _resolve_python_import(file_path, imp, root)
                    if resolved:
                        targets.append(str(resolved))
                        
        # Save unique edges
        for t in set(targets):
            if t != rel and t in dependencies:  # ensure it exists in project
                dependencies[rel].append(t)
                if rel not in dependents[t]:
                    dependents[t].append(rel)
                    
    return dependencies, dependents


@mcp.tool(
    name="build_dependency_graph",
    description="Scan files and construct a complete mapping of dependencies and references in the project.",
)
def build_dependency_graph(path: str = ".") -> str:
    """Scan codebase imports and return dependency graph JSON."""
    root = validate_path(path)
    deps, deps_in = _get_graph(root)
    
    total_edges = sum(len(v) for v in deps.values())
    summary = {
        "total_files": len(deps),
        "total_connections": total_edges,
        "graph": deps
    }
    return json.dumps(summary, indent=2)


@mcp.tool(
    name="impact_analysis",
    description="Calculate direct and transitive downstream files affected if a given file is modified.",
)
def impact_analysis(file_path: str, path: str = ".") -> str:
    """Find all files that depend on the target file, directly or transitively (BFS traversal)."""
    root = validate_path(path)
    target_path = Path(file_path)
    
    # Try to resolve relative to root or as is
    resolved_target = target_path
    if not resolved_target.is_file():
        resolved_target = root / target_path
        
    if not resolved_target.is_file():
        return f"File '{file_path}' not found."
        
    rel_target = str(resolved_target.relative_to(root))
    
    dependencies, dependents = _get_graph(root)
    
    if rel_target not in dependents:
        return f"File '{rel_target}' is not tracked in the dependency graph (or has no suffix dependencies)."
        
    # Traverse using BFS to find direct and transitive dependents
    queue = [rel_target]
    visited = set()
    direct = dependents[rel_target]
    transitive = []
    
    while queue:
        current = queue.pop(0)
        for parent in dependents.get(current, []):
            if parent not in visited and parent != rel_target:
                visited.add(parent)
                queue.append(parent)
                if parent not in direct:
                    transitive.append(parent)
                    
    report = [
        f"# 🚨 Downstream Impact Analysis: `{rel_target}`",
        f"**Direct Dependents (1st level):** {len(direct)} files",
        f"**Transitive Dependents (recursive):** {len(transitive)} files",
        f"**Total Affected Files:** {len(direct) + len(transitive)} files",
        ""
    ]
    
    if direct:
        report.append("### 🔗 Direct Impact (Must review directly)")
        for d in sorted(direct):
            report.append(f"- `{d}`")
        report.append("")
        
    if transitive:
        report.append("### 🌪️ Transitive Impact (Check for regression/refactoring side effects)")
        for t in sorted(transitive):
            report.append(f"- `{t}`")
        report.append("")
        
    if not direct and not transitive:
        report.append("✅ **Isolation verified:** This file has no downstream dependents. It is safe to refactor without breaking other code.")
        
    return "\n".join(report)
