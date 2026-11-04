#!/usr/bin/env python3
"""
Unit tests for dev-mcp optimizations:
- Fast AST & mtime caching in brain/dependency.py
- Blast-Radius-First refactoring output
- Desktop automation tools in tools/desktop_ops.py
- Automated Git pre-commit hook installer in tools/git_ops.py
- Tool Profile filtering in server.py
"""

import os
import shutil
import sys
import unittest
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import app
import brain.dependency as dep
import tools.desktop_ops as desktop
from tools.git_ops import install_git_hooks
import server


class TestDevMCPOptimizations(unittest.TestCase):

    def setUp(self):
        app._project_context = None
        self.sandbox = (project_root / "test_sandbox_opt").resolve()
        if self.sandbox.exists():
            shutil.rmtree(self.sandbox)
        self.sandbox.mkdir(parents=True, exist_ok=True)

        # Setup mock git repo
        import subprocess
        subprocess.run(["git", "init", "-b", "main"], cwd=str(self.sandbox), check=True, capture_output=True)

    def tearDown(self):
        if self.sandbox.exists():
            shutil.rmtree(self.sandbox)

    def test_dependency_mtime_caching(self):
        """Verify that dependency parsing caches results and avoids re-reading unchanged files."""
        # Create mock python files with imports
        a = self.sandbox / "module_a.py"
        b = self.sandbox / "module_b.py"
        a.write_text("import module_b\n", encoding="utf-8")
        b.write_text("x = 42\n", encoding="utf-8")

        # First run: populates cache
        deps1, deps_in1 = dep._get_graph(self.sandbox)
        self.assertIn("module_a.py", deps1)
        self.assertIn("module_b.py", deps1["module_a.py"])

        canonical_a = str(a.resolve())
        self.assertIn(canonical_a, dep._FILE_PARSE_CACHE)
        cached_mtime, cached_imports = dep._FILE_PARSE_CACHE[canonical_a]
        self.assertEqual(cached_imports, ["module_b"])

        # Second run: should hit cache without error
        deps2, deps_in2 = dep._get_graph(self.sandbox)
        self.assertEqual(deps1, deps2)

    def test_blast_radius_first_refactoring(self):
        """Verify enhanced impact analysis report with risk assessment and refactoring playbook."""
        auth = self.sandbox / "auth.py"
        route = self.sandbox / "route.py"
        test_file = self.sandbox / "test_auth.py"

        auth.write_text("def verify_user(): return True\n", encoding="utf-8")
        route.write_text("import auth\ndef get(): return auth.verify_user()\n", encoding="utf-8")
        test_file.write_text("import auth\ndef test(): assert auth.verify_user()\n", encoding="utf-8")

        report = dep.impact_analysis("auth.py", path=str(self.sandbox))
        self.assertIn("Blast Radius Assessment", report)
        self.assertIn("Affected Test Suites", report)
        self.assertIn("Blast-Radius-First Refactoring Playbook", report)
        self.assertIn("test_auth.py", report)
        self.assertIn("route.py", report)

    def test_git_hook_installer(self):
        """Verify install_git_hooks creates executable pre-commit hook."""
        res = install_git_hooks(repo_path=str(self.sandbox), hook_type="pre-commit")
        self.assertIn("Successfully installed pre-commit hook", res)

        hook_file = self.sandbox / ".git" / "hooks" / "pre-commit"
        self.assertTrue(hook_file.is_file())
        self.assertTrue(os.access(hook_file, os.X_OK))

    def test_desktop_ops_tools_registered(self):
        """Verify that desktop tools are callable."""
        status = desktop.desktop_status()
        self.assertTrue("linux" in status.lower() or "ok" in status.lower())

    def test_server_profile_resolution(self):
        """Verify tool profile resolver maps profiles correctly."""
        env_profile, mods = server._resolve_profile_modules()
        self.assertTrue(len(mods) > 0)


if __name__ == "__main__":
    unittest.main()
