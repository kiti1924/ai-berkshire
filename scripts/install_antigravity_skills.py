#!/usr/bin/env python3
"""
Dedicated installer for importing AI Berkshire skills to Antigravity global configuration.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_antigravity_skills_dir() -> Path:
    # デフォルトのグローバルカスタマイズルート: ~/.gemini/config/skills
    # Windows: C:\\Users\\<Username>\\.gemini\\config\\skills
    return Path(os.path.expanduser("~/.gemini/config/skills")).resolve()

def sync_codex_skills():
    """インストールの前に、最新のスキルセットを codex-skills へビルドする"""
    sync_script = ROOT / "scripts" / "sync-codex-skills.py"
    if sync_script.exists():
        print("1. スキルをビルド中 (sync-codex-skills.py)...")
        # Windowsの環境互換性を考慮して sys.executable で実行
        result = subprocess.run([sys.executable, str(sync_script)], check=True)
        if result.returncode == 0:
            print("   ✅ ビルド完了")
        else:
            print("   ❌ ビルド失敗")
            sys.exit(1)
    else:
        print("   ⚠️ sync-codex-skills.py が見つかりません。既存のビルドを使用します。")

def install_skills():
    dst_dir = get_antigravity_skills_dir()
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    src_dir = ROOT / "codex-skills"
    if not src_dir.exists():
        print(f"❌ ソースディレクトリ {src_dir} が存在しません。sync-codex-skills.py を実行してください。")
        sys.exit(1)
        
    print(f"2. スキルを Antigravity グローバルディレクトリにコピー中...")
    print(f"   ターゲット: {dst_dir}")
    
    installed_count = 0
    for skill_path in src_dir.iterdir():
        if skill_path.is_dir():
            target_path = dst_dir / skill_path.name
            
            # 既存のスキルディレクトリがあればクリーンアップしてコピー
            if target_path.exists():
                shutil.rmtree(target_path)
                
            shutil.copytree(skill_path, target_path)
            print(f"   [+] {skill_path.name}")
            installed_count += 1
            
    print(f"\n✅ インストール完了: {installed_count} 個のスキルを {dst_dir} に配備しました。")

def main():
    sync_codex_skills()
    install_skills()

if __name__ == "__main__":
    main()
