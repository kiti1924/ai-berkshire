#!/usr/bin/env python3
"""Generate Codex skills from AI Berkshire Claude command files in Japanese."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / "skills"
CODEX_SKILLS = ROOT / "codex-skills"

def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :].lstrip("\n")

def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback

def yaml_quote(value: str) -> str:
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'

def metadata_for(name: str, source_name: str, source_text: str) -> str:
    existing, body = split_frontmatter(source_text)
    if existing:
        has_name = re.search(r"(?m)^name:\s*", existing) is not None
        has_description = re.search(r"(?m)^description:\s*", existing) is not None
        lines = []
        if not has_name:
            lines.append(f"name: {name}")
        if not has_description:
            title = first_heading(body, name)
            lines.append(
                "description: "
                + yaml_quote(f"AI Berkshire Skill: {title}（原本: skills/{source_name}）")
            )
        lines.append(existing.rstrip())
        return "---\n" + "\n".join(lines) + "\n---\n\n"

    title = first_heading(source_text, name)
    description = f"AI Berkshire Skill: {title}（原本: skills/{source_name}）"
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {yaml_quote(description)}\n"
        "---\n\n"
    )

def codex_body(name: str, source_name: str, source_text: str) -> str:
    _, body = split_frontmatter(source_text)
    note = (
        "## Codexアダプター注記\n\n"
        f"このSkillは`skills/{source_name}`から生成され、Claude CodeとCodexで"
        "同じ正本のワークフローを共有する。\n\n"
        "- `$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う。\n"
        "- Windows環境のPowerShellでファイル（SKILL.mdや参照資料）を読み取るコマンドを実行する際は、"
        "文字化け（CP932/Unicode誤認識）を防ぐため、必ず `Get-Content -Encoding utf8 -Raw <ファイルパス>` "
        "または `python -c \"import pathlib; print(pathlib.Path(r'<ファイルパス>').read_text(encoding='utf-8'))\"` を使用すること。\n"
        "- 調査レポート等のファイル書き出し指示（例: `reports/{会社名}/...`）がある場合は、単に会話上にMarkdownを出力して終了せず、"
        "必ずファイル書き込みツールまたはシェルコマンド（`mkdir -p reports/{会社名}` および ファイル書き込み）を実行して実際にファイルとして保存すること。\n"
        "- 正本がTask、Agent、WebSearch、Bash、Read、WriteなどClaude Code固有の機能を"
        "参照する場合は、このセッションで利用できる最も近いCodex機能へ置き換える。"
        "必要に応じてサブエージェント、Web検索、ローカルツール実行用のシェルコマンド、"
        "ワークスペース内の通常のファイル編集を使う。\n"
        "- 共通ツールは本リポジトリの`tools/`から使用する。"
        "`~/ai-berkshire/tools/...`を参照するコマンドは、リポジトリを"
        "`~/ai-berkshire`へチェックアウトした前提である。必要なら現在のワークスペースのパスを優先する。\n"
        "- `AGENTS.md`の調査品質規則を維持する。財務データを照合し、"
        "評価と計算には精密計算ツールを使い、不確実性と情報源の不足を明示する。\n\n"
    )
    return note + body.rstrip() + "\n"

def main() -> None:
    check = "--check" in sys.argv[1:]
    unknown_args = [arg for arg in sys.argv[1:] if arg != "--check"]
    if unknown_args:
        joined = ", ".join(unknown_args)
        raise SystemExit(f"Unknown argument(s): {joined}")

    if not check:
        CODEX_SKILLS.mkdir(exist_ok=True)

    count = 0
    stale: list[str] = []
    for source in sorted(CLAUDE_SKILLS.glob("*.md")):
        name = source.stem
        source_text = source.read_text(encoding="utf-8-sig")
        target_dir = CODEX_SKILLS / name
        target = target_dir / "SKILL.md"
        content = metadata_for(name, source.name, source_text) + codex_body(
            name, source.name, source_text
        )
        if check:
            if not target.exists() or target.read_text(encoding="utf-8-sig") != content:
                stale.append(str(target.relative_to(ROOT)))
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        count += 1

    if check:
        if stale:
            print("Codex skills are out of date:")
            for path in stale:
                print(f"  {path}")
            raise SystemExit(1)
        print(f"Checked {count} Codex skills in {CODEX_SKILLS.relative_to(ROOT)}")
        return

    print(f"Generated {count} Codex skills in {CODEX_SKILLS.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
