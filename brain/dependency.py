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


# In-memory mtime cache to avoid re-reading and re-parsing unchanged files
# Key: canonical file path, Value: (mtime, list_of_raw_imports)
_FILE_PARSE_CACHE: dict[str, tuple[float, list[str]]] = {}

# Graph-level cache: key is root string, value is (cache_timestamp, dependencies, dependents)
_ROOT_GRAPH_CACHE: dict[str, tuple[float, dict[str, list[str]], dict[str, list[str]]]] = {}


def _get_graph(root: Path, force_refresh: bool = False) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Scan root files and build adjacency lists: dependencies (outgoing) and dependents (incoming).
    
    Uses mtime-based in-memory caching to eliminate disk reads and regex overhead on unchanged files.
    """
    dependencies: dict[str, list[str]] = {}
    dependents: dict[str, list[str]] = {}
    
    js_import_re = re.compile(r'\b(?:import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))')
    py_import_re = re.compile(r'\b(?:import\s+([\w\.]+)|from\s+([\w\.]+)\s+import)')
    
    all_files: list[tuple[Path, str, str, float]] = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        
        for name in filenames:
            file_path = Path(dirpath) / name
            suffix = file_path.suffix
            if suffix not in (".py", ".ts", ".tsx", ".js", ".jsx"):
                continue
            rel = str(file_path.relative_to(root))
            try:
                mtime = file_path.stat().st_mtime
            except OSError:
                continue
            all_files.append((file_path, rel, suffix, mtime))
            dependencies[rel] = []
            dependents[rel] = []
            
    # Parse each file using mtime cache
    for file_path, rel, suffix, mtime in all_files:
        canonical_key = str(file_path.resolve())
        cached_entry = _FILE_PARSE_CACHE.get(canonical_key)
        
        if cached_entry is not None and cached_entry[0] == mtime and not force_refresh:
            raw_imports = cached_entry[1]
        else:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
                
            raw_imports = []
            if suffix in (".js", ".jsx", ".ts", ".tsx"):
                for match in js_import_re.finditer(content):
                    imp = match.group(1) or match.group(2)
                    if imp:
                        raw_imports.append(imp)
            elif suffix == ".py":
                for match in py_import_re.finditer(content):
                    imp = match.group(1) or match.group(2)
                    if imp:
                        raw_imports.append(imp)
                        
            _FILE_PARSE_CACHE[canonical_key] = (mtime, raw_imports)
            
        # Resolve imports to relative paths
        targets: list[str] = []
        if suffix in (".js", ".jsx", ".ts", ".tsx"):
            for imp in raw_imports:
                resolved = _resolve_js_ts_import(file_path, imp, root)
                if resolved:
                    targets.append(str(resolved))
        elif suffix == ".py":
            for imp in raw_imports:
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
                    
    total_affected = len(direct) + len(transitive)
    
    # Assess Blast Radius Risk Level
    if total_affected == 0:
        risk_badge = "🟢 LOW RISK (Isolated)"
    elif total_affected <= 3:
        risk_badge = "🟡 MEDIUM RISK (Manageable)"
    else:
        risk_badge = "🔴 HIGH RISK (Critical Surface Area)"

    # Identify affected test files vs source files
    all_affected = sorted(list(set(direct + transitive)))
    test_files = [f for f in all_affected if "test" in f.lower() or "spec" in f.lower()]
    source_files = [f for f in all_affected if f not in test_files]

    report = [
        f"# 🚨 Downstream Impact Analysis: `{rel_target}`",
        f"**Blast Radius Assessment:** {risk_badge}",
        f"- **Direct Dependents (1st level):** {len(direct)} files",
        f"- **Transitive Dependents (recursive):** {len(transitive)} files",
        f"- **Total Affected Files:** {total_affected} files",
        ""
    ]
    
    if direct:
        report.append("### 🔗 Direct Impact (Must update immediately when modifying exports)")
        for d in sorted(direct):
            icon = "🧪" if d in test_files else "📄"
            report.append(f"- {icon} `{d}`")
        report.append("")
        
    if transitive:
        report.append("### 🌪️ Transitive Impact (Verify against regressions)")
        for t in sorted(transitive):
            icon = "🧪" if t in test_files else "📄"
            report.append(f"- {icon} `{t}`")
        report.append("")
        
    if test_files:
        report.append("### 🧪 Affected Test Suites")
        report.append("Run these test files to verify refactoring integrity:")
        for tf in sorted(test_files):
            report.append(f"- `{tf}`")
        report.append("")

    # Blast-Radius-First Refactoring Playbook
    if total_affected > 0:
        report.append("### 📋 Blast-Radius-First Refactoring Playbook")
        report.append("1. **Contract Lock:** Review existing exports/signatures in `" + rel_target + "`.")
        report.append("2. **Core Refactor:** Implement changes in `" + rel_target + "`.")
        report.append(f"3. **Adapt Direct Callers:** Update the {len(direct)} direct dependent files.")
        if test_files:
            report.append(f"4. **Regression Run:** Execute tests on: " + ", ".join([f"`{t}`" for t in test_files[:4]]) + ("..." if len(test_files) > 4 else ""))
        report.append("5. **Verify Transitive:** Validate that no downstream runtime contracts were broken.")
    else:
        report.append("✅ **Isolation verified:** This file has no downstream dependents. It is safe to refactor without breaking other project modules.")
        
    return "\n".join(report)
