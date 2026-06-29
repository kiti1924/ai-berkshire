#!/usr/bin/env python3
"""
Cross-platform installer for AI Berkshire skills, commands, runtime bundle, and manifest management.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_ai_berkshire_home() -> Path:
    if "AI_BERKSHIRE_HOME" in os.environ:
        return Path(os.environ["AI_BERKSHIRE_HOME"]).resolve()
    
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        return Path(local_app_data) / "ai-berkshire"
    elif sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support/ai-berkshire"))
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return Path(xdg_data) / "ai-berkshire"

def atomic_copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dst.parent) as tmp_dir:
        tmp_target = Path(tmp_dir) / dst.name
        shutil.copytree(src, tmp_target, dirs_exist_ok=True)
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(tmp_target), str(dst))

def copy_file_atomic(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=dst.parent, delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    shutil.copy2(src, tmp_path)
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp_path), str(dst))

def sync_runtime_bundle(home: Path) -> list[str]:
    home.mkdir(parents=True, exist_ok=True)
    installed_files: list[str] = []
    
    # Copy tools
    tools_src = ROOT / "tools"
    tools_dst = home / "tools"
    if tools_src.exists():
        atomic_copytree(tools_src, tools_dst)
        for p in tools_dst.rglob("*"):
            if p.is_file():
                installed_files.append(str(p.relative_to(home)))
                
    # Copy config / schemas if exist
    for sub in ["config", "schemas"]:
        src = ROOT / sub
        dst = home / sub
        if src.exists():
            atomic_copytree(src, dst)
            for p in dst.rglob("*"):
                if p.is_file():
                    installed_files.append(str(p.relative_to(home)))

    # Copy references (docs/global-market-adaptation and skills/ shared, markets, lenses)
    ref_dst = home / "references"
    docs_src = ROOT / "docs" / "global-market-adaptation"
    if docs_src.exists():
        atomic_copytree(docs_src, ref_dst / "docs" / "global-market-adaptation")
        
    skills_src = ROOT / "skills"
    if skills_src.exists():
        for sub in ["shared", "markets", "lenses"]:
            s = skills_src / sub
            if s.exists():
                atomic_copytree(s, ref_dst / sub)

    if ref_dst.exists():
        for p in ref_dst.rglob("*"):
            if p.is_file():
                installed_files.append(str(p.relative_to(home)))
                
    return installed_files

def update_manifest(home: Path, component: str, component_files: list[str]) -> None:
    manifest_path = home / "install-manifest.json"
    data = {
        "project": "ai-berkshire",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "components": {}
    }
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if isinstance(existing, dict) and "components" in existing:
                    data["components"] = existing["components"]
        except Exception:
            pass
            
    data["components"][component] = {
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "files": sorted(component_files)
    }
    
    copy_file_atomic_text(manifest_path, json.dumps(data, indent=2, ensure_ascii=False))

def copy_file_atomic_text(dst: Path, content: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=dst.parent, delete=False, encoding="utf-8") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(content)
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp_path), str(dst))

def install_claude() -> None:
    home = get_ai_berkshire_home()
    bundle_files = sync_runtime_bundle(home)
    
    dest_dir_str = os.environ.get("CLAUDE_COMMANDS_DIR", os.path.expanduser("~/.claude/commands"))
    dest_dir = Path(dest_dir_str).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    skills_dir = ROOT / "skills"
    claude_installed: list[str] = []
    if skills_dir.exists():
        for item in skills_dir.glob("*.md"):
            if item.is_file():
                target = dest_dir / item.name
                copy_file_atomic(item, target)
                claude_installed.append(str(target))
                
    update_manifest(home, "claude_commands", bundle_files + claude_installed)
    print(f"Installed Claude Code commands to {dest_dir}")
    print(f"Runtime bundle updated in {home}")

def install_codex_skills() -> None:
    home = get_ai_berkshire_home()
    bundle_files = sync_runtime_bundle(home)
    
    # Run sync-codex-skills.py first
    sync_script = ROOT / "scripts" / "sync-codex-skills.py"
    if sync_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(sync_script)], check=True)
        
    dest_dir_str = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    skills_dest_codex = Path(dest_dir_str).resolve() / "skills"
    
    skills_dest_agents = Path(os.path.expanduser("~/.agents/skills")).resolve()
    skills_dest_agents.mkdir(parents=True, exist_ok=True)
    
    codex_skills_src = ROOT / "codex-skills"
    installed: list[str] = []
    if codex_skills_src.exists():
        for skill_dir in codex_skills_src.iterdir():
            if skill_dir.is_dir():
                # Clean up legacy duplicate in ~/.codex/skills if present
                legacy_target = skills_dest_codex / skill_dir.name
                if legacy_target.exists():
                    shutil.rmtree(legacy_target, ignore_errors=True)
                    
                target_agents = skills_dest_agents / skill_dir.name
                atomic_copytree(skill_dir, target_agents)
                installed.append(str(target_agents))
                
    update_manifest(home, "codex_skills", bundle_files + installed)
    print(f"Installed Codex skills to {skills_dest_agents} (cleaned legacy copies in {skills_dest_codex})")
    print(f"Runtime bundle updated in {home}")

def install_codex_prompts() -> None:
    home = get_ai_berkshire_home()
    
    sync_script = ROOT / "scripts" / "sync-codex-prompts.py"
    if sync_script.exists():
        import subprocess
        subprocess.run([sys.executable, str(sync_script)], check=True)
        
    dest_dir_str = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    prompts_dest = Path(dest_dir_str).resolve() / "prompts"
    prompts_dest.mkdir(parents=True, exist_ok=True)
    
    prompts_src = ROOT / "codex-prompts"
    installed: list[str] = []
    if prompts_src.exists():
        for item in prompts_src.glob("*.md"):
            if item.is_file():
                target = prompts_dest / item.name
                copy_file_atomic(item, target)
                installed.append(str(target))
                
    update_manifest(home, "codex_prompts", installed)
    print(f"Installed Codex slash prompts to {prompts_dest}")

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 installer.py [claude|codex-skills|codex-prompts]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "claude":
        install_claude()
    elif cmd == "codex-skills":
        install_codex_skills()
    elif cmd == "codex-prompts":
        install_codex_prompts()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
