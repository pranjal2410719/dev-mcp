"""
Requirement Traceability and Outcome Verification Engine for Project Brain.

Provides: extract_requirements, verify_requirements, verify_outcome
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from app import mcp
from security import validate_path
from brain.todo_engine import _load_todos, _load_completed

REQUIREMENTS_FILE = "requirements.json"


def _prd_dir(project_root: Path) -> Path:
    p = project_root / ".project_brain" / "prd"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_requirements(root: Path) -> list[dict]:
    p = _prd_dir(root) / REQUIREMENTS_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_requirements(root: Path, reqs: list[dict]) -> None:
    p = _prd_dir(root) / REQUIREMENTS_FILE
    p.write_text(json.dumps(reqs, indent=2), encoding="utf-8")


@mcp.tool(
    name="extract_requirements",
    description="Parse PRD markdown files to extract structured requirements and save them into requirements.json.",
)
def extract_requirements(path: str = ".") -> str:
    """Read PRD documents, extract list items from requirements sections, and save to requirements.json."""
    root = validate_path(path)
    prd_dir = _prd_dir(root)
    
    # Check what prd files exist
    prd_files = ["PRD.md", "REQUIREMENTS.md", "SCOPE.md", "VISION.md"]
    found_content = ""
    for fname in prd_files:
        fpath = prd_dir / fname
        if fpath.is_file():
            found_content += f"\n\n=== {fname} ===\n" + fpath.read_text(encoding="utf-8")
            
    if not found_content:
        return "No PRD files found in .project_brain/prd/ (PRD.md, REQUIREMENTS.md, etc.). Please create one first."
        
    lines = found_content.splitlines()
    req_lines = []
    current_section = "General"
    
    in_target_section = False
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("#"):
            current_section = line_strip.lstrip("#").strip()
            sec_lower = current_section.lower()
            if any(k in sec_lower for k in ("requirement", "feature", "scope", "specification", "list")):
                in_target_section = True
            else:
                in_target_section = False
            continue
            
        if in_target_section and line_strip:
            if line_strip.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                clean_req = re.sub(r'^[\-\*\s\d\.]+', '', line_strip).strip()
                if len(clean_req) > 10:
                    req_lines.append((current_section, clean_req))
                    
    # Format into list of dicts
    extracted = []
    for idx, (sec, req) in enumerate(req_lines, 1):
        words = re.findall(r'\b\w{4,}\b', req.lower())
        keywords = list(set([w for w in words if w not in ("user", "system", "must", "should", "shall", "with", "have", "from", "that", "this", "will", "when")]))
        
        extracted.append({
            "id": f"REQ-{idx:03d}",
            "feature": sec,
            "requirement": req,
            "keywords": keywords,
            "status": "pending"
        })
        
    if not extracted:
        # Template requirements if none could be parsed
        extracted.append({
            "id": "REQ-001",
            "feature": "Core Feature Flow",
            "requirement": "System must capture and validate core user input fields.",
            "keywords": ["system", "capture", "validate", "input", "fields"],
            "status": "pending"
        })
        extracted.append({
            "id": "REQ-002",
            "feature": "Database Persistence",
            "requirement": "System must persist valid data objects and provide error handler states.",
            "keywords": ["persist", "data", "objects", "error", "handler"],
            "status": "pending"
        })
        
    _save_requirements(root, extracted)
    return f"Extracted and saved {len(extracted)} requirements in .project_brain/prd/requirements.json."


@mcp.tool(
    name="verify_requirements",
    description="Scan codebase to map requirement keywords and verify their implementation status and feature coverage.",
)
def verify_requirements(feature_name: str = "", path: str = ".") -> str:
    """Checks requirements in requirements.json against files in the codebase."""
    root = validate_path(path)
    reqs = _load_requirements(root)
    
    if not reqs:
        return "No structured requirements found. Run extract_requirements first to build requirements.json."
        
    if feature_name:
        reqs = [r for r in reqs if feature_name.lower() in r.get("feature", "").lower()]
        
    if not reqs:
        return f"No requirements found for feature '{feature_name}'."
        
    from brain.guardian import IGNORE_DIRS, SCAN_EXTENSIONS
    
    code_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for name in filenames:
            file_path = Path(dirpath) / name
            if file_path.suffix in SCAN_EXTENSIONS:
                code_files.append(file_path)
                
    verified_reqs = []
    total = len(reqs)
    implemented_count = 0
    
    for r in reqs:
        r_id = r.get("id", "")
        keywords = r.get("keywords", [])
        req_text = r.get("requirement", "")
        feat = r.get("feature", "")
        
        matches = {}
        for kw in keywords:
            variations = [kw, kw.replace("_", ""), re.sub(r'_([a-z])', lambda m: m.group(1).upper(), kw)]
            variations = list(set(variations))
            
            kw_pat = re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in variations) + r')\b', re.IGNORECASE)
            
            matched_files = []
            for cf in code_files:
                try:
                    content = cf.read_text(encoding="utf-8", errors="ignore")
                    if kw_pat.search(content):
                        matched_files.append(str(cf.relative_to(root)))
                except Exception:
                    continue
            if matched_files:
                matches[kw] = matched_files[:2]
                
        match_ratio = len(matches) / len(keywords) if keywords else 0
        is_implemented = match_ratio >= 0.60
        
        status = "implemented" if is_implemented else "missing"
        if is_implemented:
            implemented_count += 1
            
        verified_reqs.append({
            "id": r_id,
            "feature": feat,
            "requirement": req_text,
            "status": status,
            "matched_keywords": list(matches.keys()),
            "missing_keywords": [k for k in keywords if k not in matches],
            "confidence": int(match_ratio * 100)
        })
        
    coverage = int((implemented_count / total) * 100) if total > 0 else 0
    
    # Save back updated statuses (best-effort)
    full_reqs = _load_requirements(root)
    for fr in full_reqs:
        for vr in verified_reqs:
            if fr["id"] == vr["id"]:
                fr["status"] = vr["status"]
                break
    _save_requirements(root, full_reqs)
    
    report = [
        f"# 📋 Requirement Traceability Matrix: {feature_name if feature_name else 'All Features'}",
        f"**Total Requirements Evaluated:** {total}",
        f"**Implemented:** {implemented_count} | **Missing:** {total - implemented_count}",
        f"**Requirement Coverage:** {coverage}%",
        ""
    ]
    
    report.append("## 🔍 Detailed Coverage Matrix")
    for vr in verified_reqs:
        icon = "✅" if vr["status"] == "implemented" else "❌"
        report.append(f"### {icon} **{vr['id']}** [{vr['feature']}] — {vr['requirement']}")
        report.append(f"- **Status:** {vr['status'].upper()} (Keyword Match: {vr['confidence']}% confidence)")
        if vr["matched_keywords"]:
            report.append(f"  - **Detected Keywords:** {', '.join(vr['matched_keywords'])}")
        if vr["missing_keywords"]:
            report.append(f"  - **Missing Keywords:** {', '.join(vr['missing_keywords'])}")
        report.append("")
        
    return "\n".join(report)


@mcp.tool(
    name="verify_outcome",
    description="Perform outcome audits verifying user flows, business goals, and objective completion based on target tasks.",
)
def verify_outcome(task_id: str, path: str = ".") -> str:
    """Traces task to high-level PRD objectives and audits implementation outcomes."""
    root = validate_path(path)
    
    # Load task details
    todos = _load_todos(root)
    task = None
    for t in todos:
        if t.get("id") == task_id:
            task = t
            break
            
    if not task:
        completed = _load_completed(root)
        for t in completed:
            if t.get("id") == task_id:
                task = t
                break
                
    if not task:
        return f"Task {task_id} not found."
        
    t_title = task.get("title", "")
    t_desc = task.get("description", "")
    
    # Extract file changes
    file_hints = re.findall(r'\b[\w\-\./]+\.(?:py|js|ts|tsx|jsx|json|html|css|toml)\b', f"{t_title} {t_desc}")
    file_hints = list(set(file_hints))
    
    files_found = []
    for f in file_hints:
        fp = Path(f)
        resolved_f = fp if fp.is_file() else root / fp
        if resolved_f.is_file():
            files_found.append(str(resolved_f.relative_to(root)))
            
    form_detected = False
    db_save_detected = False
    navigation_detected = False
    
    for f in files_found:
        try:
            content = (root / f).read_text(encoding="utf-8", errors="ignore")
            if re.search(r'\b(?:form|input|button|submit|onChange|handleSubmit|TextField)\b', content, re.IGNORECASE):
                form_detected = True
            if re.search(r'\b(?:insert|upsert|save|db|create|supabase|post|mutation|axios|fetch)\b', content, re.IGNORECASE):
                db_save_detected = True
            if re.search(r'\b(?:router|navigate|push|Link|href|route)\b', content, re.IGNORECASE):
                navigation_detected = True
        except Exception:
            continue
            
    report = [
        f"# 🎭 User Outcome Audit: `{task_id}`",
        f"**Goal:** {t_title}",
        f"**Files Evaluated:** {', '.join(files_found) if files_found else 'None'}",
        "",
        "## 🛠️ Execution Flow Auditing",
        f"- **Form Input Capture:** {'Detected (UI code present) ✓' if form_detected else 'Not detected / None needed ⚠️'}",
        f"- **Persistence & API Save:** {'Detected (DB / fetch operations present) ✓' if db_save_detected else 'Not detected / None needed ⚠️'}",
        f"- **Navigation / Success State:** {'Detected (Router / Link calls present) ✓' if navigation_detected else 'Not detected / None needed ⚠️'}",
        "",
        "## 🎯 Objective Verification Instructions",
        "If you are the AI assistant reading this dossier, verify the overall UX outcome by answering:",
        "1. **Entrypoint:** How does the user enter this flow?",
        "2. **Data validation:** Does the UI validate inputs before sending?",
        "3. **Persistence:** Where is the data stored, and what columns/tables are utilized?",
        "4. **Error handling:** What happens if the network or database call fails?",
        "",
        "Compare the target files diff against these outcomes to ensure a complete, premium implementation."
    ]
    
    return "\n".join(report)
