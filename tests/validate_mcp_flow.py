#!/usr/bin/env python3
"""
Validation Pipeline for dev-mcp.
Tests the accuracy and correctness of onboarding, planning, and verification tools:
- assess_project_readiness()
- adopt_existing_project()
- sync_workspace()
- verify_work()
- verify_requirements()
- verify_outcome()
"""

import os
import shutil
import sys
import unittest
import json
import subprocess
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Clear context cache helper
def reset_global_context():
    import app
    app._project_context = None

# Import target functions
from brain.project_readiness import assess_project_readiness, adopt_existing_project
from brain.sync_engine import sync_workspace, verify_work
from brain.requirements import extract_requirements, verify_requirements, verify_outcome

class TestMCPAccuracyPipeline(unittest.TestCase):
    
    def setUp(self):
        reset_global_context()
        self.sandbox_path = project_root / "test_sandbox"
        if self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path)
        self.sandbox_path.mkdir()
        
    def tearDown(self):
        reset_global_context()
        if self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path)

    def test_complete_onboarding_and_verification_flow(self):
        sandbox_str = str(self.sandbox_path)
        
        # --- PHASE 1: Readiness Assessment of empty / raw repo ---
        print("\n--- Phase 1: Readiness Assessment ---")
        readiness_json_str = assess_project_readiness(sandbox_str)
        readiness = json.loads(readiness_json_str)
        
        print(f"Readiness Score (Empty Repo): {readiness['readiness_score']}/100")
        self.assertLess(readiness['readiness_score'], 30, "Empty directory should score low on readiness")
        self.assertIn("README.md File", readiness['missing_components'])

        # Initialize mock legacy files to test adoption engine
        print("\nInitializing mock legacy project...")
        # 1. Create a dummy README with a project description
        readme_content = (
            "# TaskyApp\n\n"
            "TaskyApp is a simple tool to manage list items. It uses sqlite for persistence.\n\n"
            "Features:\n"
            "- Save items to database\n"
            "- Display lists on frontend\n"
        )
        (self.sandbox_path / "README.md").write_text(readme_content, encoding="utf-8")
        
        # 2. Create a mock Python database script
        db_script = (
            "import sqlite3\n"
            "def save_task(task_id, title):\n"
            "    conn = sqlite3.connect('tasks.db')\n"
            "    cursor = conn.cursor()\n"
            "    cursor.execute('INSERT INTO tasks VALUES (?, ?)', (task_id, title))\n"
            "    conn.commit()\n"
            "    conn.close()\n"
        )
        (self.sandbox_path / "database.py").write_text(db_script, encoding="utf-8")
        
        # 3. Initialize git repo in sandbox
        subprocess.run(["git", "init", "-b", "main"], cwd=sandbox_str, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=sandbox_str, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=sandbox_str, check=True)
        subprocess.run(["git", "add", "."], cwd=sandbox_str, check=True)
        subprocess.run(["git", "commit", "-m", "initial commit"], cwd=sandbox_str, check=True)
        
        reset_global_context()
        
        # --- PHASE 2: Adopt Legacy Project ---
        print("\n--- Phase 2: Adopting Legacy Repository ---")
        adoption_msg = adopt_existing_project(sandbox_str)
        print(adoption_msg)
        
        # Verify adoption outputs
        brain_dir = self.sandbox_path / ".project_brain"
        self.assertTrue(brain_dir.exists(), ".project_brain directory should be created")
        self.assertTrue((brain_dir / "prd" / "PRD.md").exists(), "PRD.md template should be generated")
        self.assertTrue((brain_dir / "todos" / "active.json").exists(), "Active tasks should be generated")
        
        # Let's inspect generated PRD.md to see if it correctly parsed the README description
        prd_text = (brain_dir / "prd" / "PRD.md").read_text(encoding="utf-8")
        self.assertIn("TaskyApp is a simple tool to manage list items.", prd_text, "PRD should adopt the README description")
        
        # --- PHASE 3: Extract Requirements ---
        print("\n--- Phase 3: Extracting Requirements ---")
        reset_global_context()
        reqs_msg = extract_requirements(sandbox_str)
        print(reqs_msg)
        
        reqs_json_path = brain_dir / "prd" / "requirements.json"
        self.assertTrue(reqs_json_path.exists(), "requirements.json should exist")
        reqs = json.loads(reqs_json_path.read_text(encoding="utf-8"))
        print(f"Extracted {len(reqs)} requirements.")
        self.assertGreater(len(reqs), 0, "Should extract at least one requirement")
        
        # Verify requirement keys
        for req in reqs:
            self.assertIn("id", req)
            self.assertIn("feature", req)
            self.assertIn("requirement", req)
            self.assertIn("keywords", req)
            self.assertIn("status", req)

        # --- PHASE 4: Workspace Sync Engine (Before changes) ---
        print("\n--- Phase 4: Syncing Workspace (Before Changes) ---")
        reset_global_context()
        sync_report = sync_workspace(sandbox_str)
        print(sync_report)
        self.assertIn("All tasks align with plan", sync_report)
        
        # --- PHASE 5: Make Code Changes & Verify Sync Heuristics ---
        print("\nMaking code changes implementing TASK-0001 (Audit legacy codebase)...")
        # Let's simulate finishing TASK-0001
        # TASK-0001 is "Audit legacy codebase file structures"
        # We simulate this by checking out a branch matching the task ID, changing files, committing.
        subprocess.run(["git", "checkout", "-b", "feature/TASK-0001-audit"], cwd=sandbox_str, capture_output=True, check=True)
        
        # Modify database.py to include audit comment or code
        db_script_updated = db_script + "\n# Audited codebase file structures - OK\n"
        (self.sandbox_path / "database.py").write_text(db_script_updated, encoding="utf-8")
        
        # Stage and commit with commit message containing TASK-0001
        subprocess.run(["git", "add", "database.py"], cwd=sandbox_str, check=True)
        subprocess.run(["git", "commit", "-m", "feat: TASK-0001 audit file structures"], cwd=sandbox_str, check=True)
        
        print("\n--- Phase 5: Syncing Workspace (After Changes) ---")
        reset_global_context()
        sync_report_after = sync_workspace(sandbox_str)
        print(sync_report_after)
        
        # Assert sync engine detected task work
        self.assertIn("TASK-0001", sync_report_after)
        self.assertIn("Current Git branch name matches task ID", sync_report_after)
        self.assertIn("Task ID found in recent commit log", sync_report_after)

        # --- PHASE 6: Sanity / Outcome Verification ---
        print("\n--- Phase 6: Sanity & Outcome Verification ---")
        reset_global_context()
        verification_report = verify_work("TASK-0001", sandbox_str)
        print(verification_report)
        self.assertIn("Verification Dossier for `TASK-0001`", verification_report)
        
        # Outcome audit flow
        outcome_report = verify_outcome("TASK-0001", sandbox_str)
        print(outcome_report)
        self.assertIn("User Outcome Audit: `TASK-0001`", outcome_report)
        
        # Requirements matrix coverage
        # Let's update requirements status through check
        req_report = verify_requirements(path=sandbox_str)
        print(req_report)
        self.assertIn("Requirement Traceability Matrix", req_report)

        print("\nAll accuracy checks completed successfully! 🎉")

if __name__ == "__main__":
    unittest.main()
