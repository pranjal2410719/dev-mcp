#!/usr/bin/env python3
"""
Unit tests for dev-mcp v2.0.0 features:
- Workspace Isolation & Workspace Lock
- Safety Modes (safe, trusted, lab)
- Shell Command Auditing & Blocklist
- Destructive File Operation Block
- Automated Workspace Creation Tool (create_project_workspace)
"""

import os
import shutil
import sys
import unittest
import json
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import app
from context import ProjectContext
from security import validate_path, get_project_root_and_safety
from tools.terminal import run_command
from tools.file_ops import delete_recursive
from brain.project_readiness import create_project_workspace

def reset_global_context():
    app._project_context = None

class TestV2Features(unittest.TestCase):
    
    def setUp(self):
        reset_global_context()
        self.sandbox_path = (project_root / "test_sandbox_v2").resolve()
        if self.sandbox_path.exists():
            shutil.rmtree(self.sandbox_path)
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        # Initialize a dummy git repository inside sandbox to prevent git commands traversing up to the parent repo
        import subprocess
        try:
            subprocess.run(["git", "init", "-b", "main"], cwd=str(self.sandbox_path), check=True, capture_output=True)
        except Exception:
            try:
                subprocess.run(["git", "init"], cwd=str(self.sandbox_path), check=True, capture_output=True)
            except Exception:
                pass
        
    def tearDown(self):
        reset_global_context()
        if self.sandbox_path.exists():
            try:
                shutil.rmtree(self.sandbox_path)
            except OSError:
                pass

    def write_config(self, safety_mode: str, path: Path = None):
        if path is None:
            path = self.sandbox_path
        brain_dir = path / ".project_brain"
        brain_dir.mkdir(parents=True, exist_ok=True)
        config_file = brain_dir / "config.yaml"
        config_file.write_text(f"safety_mode: {safety_mode}\n", encoding="utf-8")

    def test_workspace_lock_safe_mode(self):
        # Set up safe mode config
        self.write_config("safe")
        
        # Load context
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        # Verify get_project_root_and_safety returns correctly
        root, safety_mode = get_project_root_and_safety()
        self.assertEqual(root, self.sandbox_path)
        self.assertEqual(safety_mode, "safe")
        
        # Path inside should be validated
        inside_path = self.sandbox_path / "some_file.txt"
        self.assertEqual(validate_path(inside_path), inside_path)
        
        # Path outside should raise PermissionError
        outside_path = self.sandbox_path.parent / "escape.txt"
        with self.assertRaises(PermissionError) as context:
            validate_path(outside_path)
        self.assertIn("Workspace Lock Active", str(context.exception))

    def test_workspace_lock_trusted_mode(self):
        # Set up trusted mode config
        self.write_config("trusted")
        
        # Load context
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        root, safety_mode = get_project_root_and_safety()
        self.assertEqual(safety_mode, "trusted")
        
        # Path inside should be validated
        inside_path = self.sandbox_path / "some_file.txt"
        self.assertEqual(validate_path(inside_path), inside_path)
        
        # Path outside should raise PermissionError
        outside_path = self.sandbox_path.parent / "escape.txt"
        with self.assertRaises(PermissionError) as context:
            validate_path(outside_path)
        self.assertIn("Workspace Lock Active", str(context.exception))

    def test_workspace_lock_lab_mode(self):
        # Set up lab mode config
        self.write_config("lab")
        
        # Load context
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        root, safety_mode = get_project_root_and_safety()
        self.assertEqual(safety_mode, "lab")
        
        # In lab mode, validate_path falls back to original allowed base dirs check.
        # Ensure path inside sandbox is allowed
        inside_path = self.sandbox_path / "some_file.txt"
        self.assertEqual(validate_path(inside_path), inside_path)

    def test_command_safety_checks_safe_mode(self):
        self.write_config("safe")
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        # Dangerous commands should be blocked
        blocked_commands = [
            "sudo apt-get update",
            "mkfs /dev/sdb1",
            "dd if=/dev/zero of=/dev/sdb",
            "shutdown -h now",
            "reboot",
            "poweroff",
            "rm -rf some_dir",
            "rm -r some_dir",
            "rm -f some_file",
            "rm -d some_dir",
            "git reset --hard HEAD",
            "git clean -fd"
        ]
        for cmd in blocked_commands:
            with self.assertRaises(PermissionError) as context:
                run_command(cmd, workdir=str(self.sandbox_path))
            self.assertIn("Command Execution Blocked", str(context.exception))

        # Traversal '..' should be blocked
        with self.assertRaises(PermissionError) as context:
            run_command("cat ../escaped.txt", workdir=str(self.sandbox_path))
        self.assertIn("Relative path traversal '..' is forbidden", str(context.exception))

        # Absolute paths outside root should be blocked
        with self.assertRaises(PermissionError) as context:
            run_command("cat /etc/passwd", workdir=str(self.sandbox_path))
        self.assertIn("is outside the active workspace", str(context.exception))

        # Absolute paths in allowed system dirs should be permitted
        # Since run_command might actually execute standard command like `ls /bin`,
        # we check that it does not raise PermissionError.
        try:
            run_command("ls /bin", workdir=str(self.sandbox_path))
        except PermissionError:
            self.fail("Standard path under /bin was blocked, but should be allowed.")
        except Exception:
            pass # FileNotFoundError or other errors are fine, as long as it's not PermissionError

    def test_command_safety_checks_trusted_mode(self):
        self.write_config("trusted")
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        # System dangerous commands should still be blocked
        system_blocked = [
            "sudo apt-get update",
            "mkfs /dev/sdb1",
            "dd if=/dev/zero of=/dev/sdb",
            "shutdown -h now",
            "reboot",
            "poweroff",
        ]
        for cmd in system_blocked:
            with self.assertRaises(PermissionError):
                run_command(cmd, workdir=str(self.sandbox_path))

        # But rm -rf and git reset --hard are allowed in trusted mode
        # Verify they do not raise PermissionError
        try:
            res1 = run_command("git reset --hard", workdir=str(self.sandbox_path))
            self.assertNotIn("Command Execution Blocked", res1)
        except PermissionError:
            self.fail("git reset --hard should not be blocked in trusted mode")

        try:
            res2 = run_command("rm -rf temporary_test_dir", workdir=str(self.sandbox_path))
            self.assertNotIn("Command Execution Blocked", res2)
        except PermissionError:
            self.fail("rm -rf should not be blocked in trusted mode")

    def test_delete_recursive_safety(self):
        # Under safe mode, delete_recursive should raise PermissionError
        self.write_config("safe")
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        test_dir = self.sandbox_path / "to_delete"
        test_dir.mkdir(exist_ok=True)
        
        with self.assertRaises(PermissionError) as context:
            delete_recursive(str(test_dir))
        self.assertIn("Action Blocked: 'delete_recursive' is forbidden", str(context.exception))
            
        # Under trusted mode, delete_recursive should succeed
        self.write_config("trusted")
        ctx = app.load_context(self.sandbox_path)
        app.set_context(ctx)
        
        delete_recursive(str(test_dir))
        self.assertFalse(test_dir.exists())

    def test_create_project_workspace(self):
        # Try bootstrapping blank template
        workspace_name = "test_blank_project"
        result = create_project_workspace(
            name=workspace_name,
            template="blank",
            path=str(self.sandbox_path)
        )
        self.assertIn("Successfully Created", result)
        
        proj_dir = self.sandbox_path / workspace_name
        self.assertTrue(proj_dir.exists())
        self.assertTrue((proj_dir / ".git").exists())
        self.assertTrue((proj_dir / ".project_brain" / "config.yaml").exists())
        self.assertTrue((proj_dir / ".project-context.json").exists())
        
        # Check config safety mode is safe
        config_content = (proj_dir / ".project_brain" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("safety_mode: safe", config_content)

        # Try nextjs template
        nextjs_workspace = "test_nextjs_project"
        result_nextjs = create_project_workspace(
            name=nextjs_workspace,
            template="nextjs",
            path=str(self.sandbox_path)
        )
        self.assertIn("Successfully Created", result_nextjs)
        
        nextjs_dir = self.sandbox_path / nextjs_workspace
        prd_content = (nextjs_dir / ".project_brain" / "prd" / "PRD.md").read_text(encoding="utf-8")
        self.assertIn("Next.js App", prd_content)
        self.assertIn("Tailwind CSS", prd_content)

if __name__ == "__main__":
    unittest.main()
