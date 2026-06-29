#!/usr/bin/env python3
"""
Test suite for Goal 1: Installation and packaging compatibility.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def test_installation_workflow():
    print("Testing Goal 1 installation workflow...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Test paths with space and non-ASCII (Japanese)
        test_home = tmp_path / "AI Berkshire 画面" / "runtime"
        test_claude = tmp_path / "claude_commands"
        test_codex = tmp_path / "codex_home"
        test_agents_skills = tmp_path / "agents_skills"
        
        # Create a pre-existing custom user skill/command to verify non-destruction
        test_claude.mkdir(parents=True, exist_ok=True)
        (test_claude / "custom-user-command.md").write_text("# My Custom Command", encoding="utf-8")
        
        (test_agents_skills / "custom-user-skill").mkdir(parents=True, exist_ok=True)
        (test_agents_skills / "custom-user-skill" / "SKILL.md").write_text("# My Custom Skill", encoding="utf-8")

        env = os.environ.copy()
        env["AI_BERKSHIRE_HOME"] = str(test_home)
        env["CLAUDE_COMMANDS_DIR"] = str(test_claude)
        env["CODEX_HOME"] = str(test_codex)
        env["AGENTS_SKILLS_DIR"] = str(test_agents_skills)
        # Ensure API key is NOT set
        env.pop("EDINET_API_KEY", None)

        # 1. Test Claude install
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "installer.py"), "claude"]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert res.returncode == 0, f"Claude install failed: {res.stderr}"
        
        # Verify custom command is preserved
        assert (test_claude / "custom-user-command.md").exists(), "Custom Claude command was deleted!"
        # Verify installed commands exist
        assert (test_claude / "investment-research.md").exists(), "investment-research.md was not installed!"
        
        # 2. Test Codex skills install
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "installer.py"), "codex-skills"]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert res.returncode == 0, f"Codex skills install failed: {res.stderr}"
        
        # Verify custom skill is preserved
        assert (test_agents_skills / "custom-user-skill" / "SKILL.md").exists(), "Custom Codex skill was deleted!"
        assert (test_agents_skills / "investment-research" / "SKILL.md").exists(), "investment-research codex skill missing!"

        # 3. Test Codex prompts install
        cmd = [sys.executable, str(REPO_ROOT / "scripts" / "installer.py"), "codex-prompts"]
        res = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert res.returncode == 0, f"Codex prompts install failed: {res.stderr}"

        # 4. Verify Manifest
        manifest_file = test_home / "install-manifest.json"
        assert manifest_file.exists(), "install-manifest.json missing in AI_BERKSHIRE_HOME!"
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert "claude_commands" in manifest["components"]
        assert "codex_skills" in manifest["components"]
        assert "codex_prompts" in manifest["components"]

        # 5. Test idempotency (repeat installation)
        res2 = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert res2.returncode == 0, "Idempotent repeat installation failed!"

        print("Goal 1 installation tests passed successfully!")

if __name__ == "__main__":
    test_installation_workflow()
