"""
Project Onboarding, Bootstrapping, and Adoption Engine for Project Brain.

Provides: assess_project_readiness, project_readiness_report, bootstrap_project, adopt_existing_project
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from app import mcp
from security import validate_path
from context import detect_and_init_context, ProjectContext


def _is_git_repo_local(root: Path) -> bool:
    """Check if target directory is inside a Git repository."""
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.returncode == 0 and "true" in res.stdout.lower()
    except Exception:
        return False


def _check_tests_local(root: Path) -> bool:
    """Scan workspace for test directories or test files."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv", "venv", "__pycache__", "build", "dist")]
        for name in filenames:
            if "test" in name.lower() or "spec" in name.lower() or name.startswith("test_"):
                return True
    return False


def _is_populated_repo(root: Path) -> bool:
    """Check if repository has existing custom source files (excluding server setup files)."""
    from brain.guardian import IGNORE_DIRS, SCAN_EXTENSIONS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for name in filenames:
            if Path(name).suffix in SCAN_EXTENSIONS and name not in ("server.py", "app.py", "context.py", "security.py"):
                return True
    return False


def _run_readiness_audit(root: Path) -> dict[str, any]:
    """Execute the scoring checks against the workspace."""
    checklist = {
        "readme": {"found": False, "score": 10, "label": "README.md File"},
        "prd": {"found": False, "score": 20, "label": "Product Requirements (PRD)"},
        "architecture": {"found": False, "score": 15, "label": "Architecture Rules"},
        "milestones": {"found": False, "score": 15, "label": "Milestone Definitions"},
        "tasks": {"found": False, "score": 15, "label": "Task Tracking (Todos)"},
        "context": {"found": False, "score": 10, "label": "Project Context Store"},
        "git": {"found": False, "score": 5, "label": "Git Version Control"},
        "tests": {"found": False, "score": 10, "label": "Unit/Integration Tests"}
    }
    
    # 1. README check
    if root.joinpath("README.md").is_file() or root.joinpath("readme.md").is_file():
        checklist["readme"]["found"] = True
        
    # 2. PRD check
    if root.joinpath(".project_brain", "prd", "PRD.md").is_file() or root.joinpath("PRD.md").is_file() or root.joinpath("docs", "PRD.md").is_file():
        checklist["prd"]["found"] = True
        
    # 3. Context check
    ctx_path = root / ProjectContext.FILE_NAME
    if ctx_path.is_file():
        checklist["context"]["found"] = True
        
    # 4. Architecture check
    if ctx_path.is_file():
        try:
            ctx_data = json.loads(ctx_path.read_text(encoding="utf-8"))
            rules = ctx_data.get("architecture", {}).get("rules", {})
            if rules.get("forbidden_technologies") or rules.get("required_technologies"):
                checklist["architecture"]["found"] = True
        except Exception:
            pass
    if not checklist["architecture"]["found"]:
        if root.joinpath("architecture.json").is_file() or root.joinpath("architecture.yaml").is_file() or root.joinpath(".project_brain", "config.yaml").is_file():
            checklist["architecture"]["found"] = True
            
    # 5. Milestones check
    milestones_path = root / ".project_brain" / "phases" / "milestones.json"
    if milestones_path.is_file():
        try:
            mils = json.loads(milestones_path.read_text(encoding="utf-8"))
            if mils:
                checklist["milestones"]["found"] = True
        except Exception:
            pass
    if not checklist["milestones"]["found"] and ctx_path.is_file():
        try:
            ctx_data = json.loads(ctx_path.read_text(encoding="utf-8"))
            if ctx_data.get("milestones"):
                checklist["milestones"]["found"] = True
        except Exception:
            pass
            
    # 6. Tasks check
    tasks_path = root / ".project_brain" / "todos" / "active.json"
    if tasks_path.is_file():
        try:
            tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
            if tasks:
                checklist["tasks"]["found"] = True
        except Exception:
            pass
    if not checklist["tasks"]["found"] and ctx_path.is_file():
        try:
            ctx_data = json.loads(ctx_path.read_text(encoding="utf-8"))
            if ctx_data.get("active_tasks"):
                checklist["tasks"]["found"] = True
        except Exception:
            pass
            
    # 7. Git check
    if _is_git_repo_local(root):
        checklist["git"]["found"] = True
        
    # 8. Tests check
    if _check_tests_local(root):
        checklist["tests"]["found"] = True
        
    # Compute score
    total_score = sum(val["score"] for val in checklist.values() if val["found"])
    
    missing = [key for key, val in checklist.items() if not val["found"]]
    
    return {
        "score": total_score,
        "checklist": checklist,
        "missing": missing
    }


@mcp.tool(
    name="assess_project_readiness",
    description="Scan the workspace and evaluate its onboarding readiness score (0-100%) against required Project Brain documents.",
)
def assess_project_readiness(path: str = ".") -> str:
    """Analyze the repository metadata and return a JSON assessment of what Project Brain requirements are missing."""
    root = validate_path(path)
    audit = _run_readiness_audit(root)
    
    score = audit["score"]
    level = "Level 0: Unknown Repo"
    if score >= 85:
        level = "Level 4: AI Ready"
    elif score >= 70:
        level = "Level 3: Trackable"
    elif score >= 50:
        level = "Level 2: Structured"
    elif score >= 20:
        level = "Level 1: Documented"
        
    # Standard health-score checks
    if audit["score"] >= 85 and _check_tests_local(root):
        level = "Level 5: Autonomous Ready"
        
    # Detect appropriate onboarding commands based on repository state
    onboarding_commands = []
    if score < 80:
        if _is_populated_repo(root):
            onboarding_commands.append(f"adopt_existing_project(path=\"{root}\")")
        else:
            onboarding_commands.append(f"bootstrap_project(path=\"{root}\")")
        onboarding_commands.append(f"extract_requirements(path=\"{root}\")")
        onboarding_commands.append(f"start_session(path=\"{root}\")")
    else:
        onboarding_commands.append(f"start_session(path=\"{root}\")")

    output = {
        "project": root.name,
        "readiness_score": score,
        "readiness_level": level,
        "missing_components": [audit["checklist"][m]["label"] for m in audit["missing"]],
        "recommendations": [f"Create {audit['checklist'][m]['label']}" for m in audit["missing"]],
        "next_steps_commands": onboarding_commands
    }
    
    return json.dumps(output, indent=2)


@mcp.tool(
    name="project_readiness_report",
    description="Generate a formatted Markdown project readiness report showing missing files, scoring audit, and recommended actions.",
)
def project_readiness_report(path: str = ".") -> str:
    """Generate a clean project readiness status report."""
    root = validate_path(path)
    audit = _run_readiness_audit(root)
    
    score = audit["score"]
    level = "Level 0: Unknown Repo ❌"
    if score >= 85:
        level = "Level 4: AI Ready ✅"
    elif score >= 70:
        level = "Level 3: Trackable ⚠️"
    elif score >= 50:
        level = "Level 2: Structured 🛠️"
    elif score >= 20:
        level = "Level 1: Documented 📄"
        
    if score >= 85 and _check_tests_local(root):
        level = "Level 5: Autonomous Ready 🚀"
        
    report = [
        f"# 📋 Project Readiness Report: `{root.name}`",
        f"**Readiness Score:** {score}/100 | **Maturity Level:** {level}",
        "",
        "## 📊 Scoring Breakdown Matrix",
        "| Component | Target Weight | Found? | Points Earned |",
        "|---|---|---|---|",
    ]
    
    for key, val in audit["checklist"].items():
        found_marker = "✓ Yes" if val["found"] else "✗ No"
        earned = val["score"] if val["found"] else 0
        report.append(f"| {val['label']} | {val['score']} | {found_marker} | {earned} |")
        
    report.append("")
    
    if audit["missing"]:
        report.extend([
            "## 🚨 Missing Components & Recommendations",
            "The repository is missing project tracking structures. Run the following actions to bootstrap your workspace:",
            ""
        ])
        for key in audit["missing"]:
            comp = audit["checklist"][key]
            if key == "prd":
                report.append(f"- **{comp['label']}**: Place a `PRD.md` functional requirements specification inside `.project_brain/prd/`.")
            elif key == "architecture":
                report.append(f"- **{comp['label']}**: Add rules under `architecture.rules` inside `.project-context.json` or create `.project_brain/config.yaml`.")
            elif key == "milestones":
                report.append(f"- **{comp['label']}**: Define project phases or milestones via `add_milestone`.")
            elif key == "tasks":
                report.append(f"- **{comp['label']}**: Create active tasks in the todo engine using `create_task`.")
            elif key == "context":
                report.append(f"- **{comp['label']}**: Run `init_context` to auto-detect codebase languages and stack.")
            elif key == "git":
                report.append(f"- **{comp['label']}**: Initialize git in the workspace directory (`git init`).")
            elif key == "tests":
                report.append(f"- **{comp['label']}**: Write unit or integration tests for the codebase modules.")
            else:
                report.append(f"- **{comp['label']}**: Create required file: `{key}`.")
        
        setup_cmd = f"adopt_existing_project(path=\"{root}\")" if _is_populated_repo(root) else f"bootstrap_project(path=\"{root}\")"
        report.extend([
            "",
            "⚙️ **Recommended Next Onboarding Commands:**",
            "Please execute the following sequence of tool calls to onboard this repository:",
            "```text",
            f"1. {setup_cmd}",
            f"2. extract_requirements(path=\"{root}\")",
            f"3. start_session(path=\"{root}\")",
            "```"
        ])
    else:
        report.extend([
            "## 🎉 Project is Fully Onboarded",
            "Your workspace contains all structures and is ready for autonomous Tech Lead workflows.",
            "Start your coding session using `start_session()`."
        ])
        
    return "\n".join(report)


@mcp.tool(
    name="bootstrap_project",
    description="Auto-generate template files and directories (PRD, milestones, active tasks, config yaml) to instantly onboard an unknown repository.",
)
def bootstrap_project(path: str = ".") -> str:
    """Initialize folders and write standard boilerplates/templates for missing project brain files."""
    root = validate_path(path)
    
    created = []
    
    # 1. Initialize context
    ctx = detect_and_init_context(root)
    created.append(ProjectContext.FILE_NAME)
    
    # Configure default architecture rules schema if empty
    rules = ctx.get("architecture.rules", {})
    if not rules.get("forbidden_technologies") and not rules.get("required_technologies"):
        ctx.set("architecture.rules.forbidden_technologies", ["redux", "firebase"])
        ctx.set("architecture.rules.required_technologies", [])
        created.append(f"{ProjectContext.FILE_NAME} (configured default rules)")
        
    # 2. Build folder structure
    prd_dir = root / ".project_brain" / "prd"
    phases_dir = root / ".project_brain" / "phases"
    todos_dir = root / ".project_brain" / "todos"
    
    prd_dir.mkdir(parents=True, exist_ok=True)
    phases_dir.mkdir(parents=True, exist_ok=True)
    todos_dir.mkdir(parents=True, exist_ok=True)
    
    # 2b. Create config.yaml if missing
    config_file = root / ".project_brain" / "config.yaml"
    if not config_file.is_file():
        cfg_yaml = (
            "project_type: auto\n"
            "language: auto\n"
            "framework: auto\n"
            "readiness_threshold: 80\n"
            "verification_threshold: 85\n"
            "auto_sync: true\n"
        )
        config_file.write_text(cfg_yaml, encoding="utf-8")
        created.append(".project_brain/config.yaml (workspace config initialized)")
        
    # 3. Create template PRD.md
    prd_file = prd_dir / "PRD.md"
    if not prd_file.is_file():
        prd_template = (
            f"# Product Requirements Document: {root.name}\n\n"
            "## 1. Product Vision & Goals\n"
            "- Define the core problem this project solves.\n"
            "- Detail the user personas and success criteria.\n\n"
            "## 2. Scope & Boundaries\n"
            "- What features are in scope for the initial version?\n"
            "- What features are strictly out of scope?\n\n"
            "## 3. Functional Requirements\n"
            "List specific functional guidelines under this section for requirements parser:\n"
            "- [ ] REQ-001: User can run local sessions and retrieve a project status dashboard.\n"
            "- [ ] REQ-002: Codebase validator enforces conventional constraints and structures.\n\n"
            "## 4. Technical Specifications\n"
            "- Define your target frontend frameworks, libraries, database engines, and deployment services.\n"
        )
        prd_file.write_text(prd_template, encoding="utf-8")
        created.append(".project_brain/prd/PRD.md (template created)")
        
    # 4. Create milestones.json template
    milestones_file = phases_dir / "milestones.json"
    if not milestones_file.is_file():
        m_data = [
            {
                "name": "Phase 1 - Bootstrap & Setup",
                "target": "2026-07-01",
                "status": "in_progress",
                "features": ["Initialize workspace structures", "Setup project configuration"]
            }
        ]
        milestones_file.write_text(json.dumps(m_data, indent=2), encoding="utf-8")
        created.append(".project_brain/phases/milestones.json (milestone created)")
        
    # 5. Create phases.json template
    phases_file = phases_dir / "phases.json"
    if not phases_file.is_file():
        p_data = {
            "phases": [
                {
                    "name": "Phase 1 - Bootstrap & Setup",
                    "description": "Establish workspace structure and configurations",
                    "status": "active",
                    "tasks": []
                }
            ],
            "current_phase": "Phase 1 - Bootstrap & Setup"
        }
        phases_file.write_text(json.dumps(p_data, indent=2), encoding="utf-8")
        created.append(".project_brain/phases/phases.json (phases log initialized)")
        
    # 6. Create active.json todo template
    active_todo_file = todos_dir / "active.json"
    if not active_todo_file.is_file():
        t_data = [
            {
                "id": "TASK-0001",
                "title": "Onboard and configure project brain guidelines",
                "phase": "Phase 1 - Bootstrap & Setup",
                "priority": "critical",
                "status": "pending",
                "depends_on": [],
                "description": "Complete the PRD requirements and run start_session to initialize.",
                "created": "2026-06-18T12:00:00"
            }
        ]
        active_todo_file.write_text(json.dumps(t_data, indent=2), encoding="utf-8")
        created.append(".project_brain/todos/active.json (initial onboarding task created)")
        
    ctx = ProjectContext(root)
    ctx.set("project.current_phase", "Phase 1 - Bootstrap & Setup")
    ctx.set("active_tasks", [
        {
            "id": "TASK-0001",
            "description": "Onboard and configure project brain guidelines",
            "status": "pending",
            "phase": "Phase 1 - Bootstrap & Setup",
            "priority": "critical"
        }
    ])
    
    return (
        f"🎉 **Bootstrapping Complete!** The following components were initialized:\n"
        + "\n".join(f"- {c}" for c in created) + "\n\n"
        "### Next Recommended Steps:\n"
        "1. Open `.project_brain/prd/PRD.md` and define your project requirements.\n"
        "2. Run `extract_requirements()` to parse the PRD bullet points.\n"
        "3. Run `start_session()` to begin development."
    )


@mcp.tool(
    name="adopt_existing_project",
    description="Scan an existing legacy codebase (directories, package lists, readmes) and generate context, PRDs, milestones, and audit tasks.",
)
def adopt_existing_project(path: str = ".") -> str:
    """Analyze an existing codebase, extract product metadata, and generate custom Project Brain configurations."""
    root = validate_path(path)
    created = []
    
    # 1. Initialize context based on detection
    ctx = detect_and_init_context(root)
    created.append(ProjectContext.FILE_NAME)
    
    # Scan readme if exists
    readme_content = ""
    readme_path = root / "README.md" if root.joinpath("README.md").is_file() else root / "readme.md"
    if readme_path.is_file():
        readme_content = readme_path.read_text(encoding="utf-8", errors="ignore")
        
    # Extract vision from README first 3 paragraphs
    vision_text = "Define the core problem this project solves and the user success criteria."
    if readme_content:
        paragraphs = [p.strip() for p in readme_content.split("\n\n") if p.strip() and not p.startswith("#")]
        if paragraphs:
            vision_text = paragraphs[0]
            if len(paragraphs) > 1 and len(vision_text) < 100:
                vision_text += "\n" + paragraphs[1]
                
    # Detect tech stack
    langs = ctx.get("tech_stack.languages", [])
    frameworks = ctx.get("tech_stack.frameworks", [])
    tools = ctx.get("tech_stack.tools", [])
    tech_spec_text = (
        f"- Languages: {', '.join(langs) if langs else 'Not detected'}\n"
        f"- Frameworks: {', '.join(frameworks) if frameworks else 'Not detected'}\n"
        f"- Tools/Infra: {', '.join(tools) if tools else 'Not detected'}\n"
    )
    
    # Configure default architecture rules
    ctx.set("architecture.rules.forbidden_technologies", ["redux", "firebase"])
    ctx.set("architecture.rules.required_technologies", [])
    
    # 2. Build directories
    prd_dir = root / ".project_brain" / "prd"
    phases_dir = root / ".project_brain" / "phases"
    todos_dir = root / ".project_brain" / "todos"
    
    prd_dir.mkdir(parents=True, exist_ok=True)
    phases_dir.mkdir(parents=True, exist_ok=True)
    todos_dir.mkdir(parents=True, exist_ok=True)
    
    # config.yaml
    config_file = root / ".project_brain" / "config.yaml"
    if not config_file.is_file():
        cfg_yaml = (
            "project_type: legacy\n"
            f"language: {langs[0] if langs else 'auto'}\n"
            f"framework: {frameworks[0] if frameworks else 'auto'}\n"
            "readiness_threshold: 80\n"
            "verification_threshold: 85\n"
            "auto_sync: true\n"
        )
        config_file.write_text(cfg_yaml, encoding="utf-8")
        created.append(".project_brain/config.yaml")
        
    # 3. Create adopted PRD.md
    prd_file = prd_dir / "PRD.md"
    if not prd_file.is_file():
        prd_content = (
            f"# Product Requirements Document: {root.name} (Adopted)\n\n"
            "## 1. Product Vision & Goals\n"
            f"{vision_text}\n\n"
            "## 2. Scope & Boundaries\n"
            "- In Scope: Maintenance and expansion of existing codebase features.\n"
            "- Out of Scope: Total refactoring without prior task registration.\n\n"
            "## 3. Functional Requirements\n"
            "List specific functional requirements under this section for parser:\n"
            "- [ ] REQ-001: Maintain current system features and verify new modules.\n"
            "- [ ] REQ-002: Write tests for all newly introduced modules.\n\n"
            "## 4. Technical Specifications\n"
            f"{tech_spec_text}"
        )
        prd_file.write_text(prd_content, encoding="utf-8")
        created.append(".project_brain/prd/PRD.md (Adoption spec generated)")
        
    # 4. Generate Adoption Phase & milestones
    milestones_file = phases_dir / "milestones.json"
    if not milestones_file.is_file():
        m_data = [
            {
                "name": "Phase 1 - Legacy Code Integration",
                "target": "TBD",
                "status": "in_progress",
                "features": ["Audit codebase file structures", "Configure architecture conventions"]
            }
        ]
        milestones_file.write_text(json.dumps(m_data, indent=2), encoding="utf-8")
        created.append(".project_brain/phases/milestones.json")
        
    phases_file = phases_dir / "phases.json"
    if not phases_file.is_file():
        p_data = {
            "phases": [
                {
                    "name": "Phase 1 - Legacy Code Integration",
                    "description": "Scan and maintain existing codebase modules",
                    "status": "active",
                    "tasks": []
                }
            ],
            "current_phase": "Phase 1 - Legacy Code Integration"
        }
        phases_file.write_text(json.dumps(p_data, indent=2), encoding="utf-8")
        created.append(".project_brain/phases/phases.json")
        
    # 5. Create initial adoption task list
    active_todo_file = todos_dir / "active.json"
    if not active_todo_file.is_file():
        t_data = [
            {
                "id": "TASK-0001",
                "title": "Audit legacy codebase file structures",
                "phase": "Phase 1 - Legacy Code Integration",
                "priority": "high",
                "status": "pending",
                "depends_on": [],
                "description": "Perform dependency scans and review codebase readiness score.",
                "created": datetime.now().isoformat()
            },
            {
                "id": "TASK-0002",
                "title": "Configure project architecture rules",
                "phase": "Phase 1 - Legacy Code Integration",
                "priority": "medium",
                "status": "pending",
                "depends_on": ["TASK-0001"],
                "description": "Define forbidden and required technologies inside configuration.",
                "created": datetime.now().isoformat()
            }
        ]
        active_todo_file.write_text(json.dumps(t_data, indent=2), encoding="utf-8")
        created.append(".project_brain/todos/active.json (Adoption tasks created)")
        
    # Synchronize mirrored list in context
    ctx = ProjectContext(root)
    ctx.set("project.current_phase", "Phase 1 - Legacy Code Integration")
    ctx.set("active_tasks", [
        {
            "id": "TASK-0001",
            "description": "Audit legacy codebase file structures",
            "status": "pending",
            "phase": "Phase 1 - Legacy Code Integration",
            "priority": "high"
        },
        {
            "id": "TASK-0002",
            "description": "Configure project architecture rules",
            "status": "pending",
            "phase": "Phase 1 - Legacy Code Integration",
            "priority": "medium"
        }
    ])
    
    return (
        f"🤖 **Legacy Project Adoption Complete!** The following components were generated:\n"
        + "\n".join(f"- {c}" for c in created) + "\n\n"
        "### Next Recommended Actions:\n"
        "1. Open `.project_brain/prd/PRD.md` to customize the drafted vision and requirements.\n"
        "2. Run `extract_requirements()` to parse the PRD.\n"
        "3. Run `start_session()` to initialize your first development sprint."
    )
