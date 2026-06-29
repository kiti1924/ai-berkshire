#!/usr/bin/env python3
"""AI Berkshire日本語版のlocale契約と生成物整合を検査する。"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "localization.yaml"
ALLOWLIST_PATH = ROOT / "docs" / "localization" / "chinese-allowlist.yaml"
GLOSSARY_PATH = ROOT / "docs" / "localization" / "glossary.md"
CANONICAL_SKILLS = ROOT / "skills"
CODEX_SKILLS = ROOT / "codex-skills"
CODEX_PROMPTS = ROOT / "codex-prompts"
SYNC_SKILLS = ROOT / "scripts" / "sync-codex-skills.py"
SYNC_PROMPTS = ROOT / "scripts" / "sync-codex-prompts.py"

REQUIRED_CONFIG_VALUES = {
    "output_language": "ja",
    "locale": "ja-JP",
    "timezone": "Asia/Tokyo",
    "writing_style": "da-dearu",
    "final_output_language": "ja",
    "parse_existing_chinese_reports": "true",
    "bulk_translate_existing_reports": "false",
}

CODEX_ONLY_SKILLS = {"investment-memo-craft"}

DISALLOWED_GENERATED_PHRASES = (
    "## Codex adapter note",
    "This skill is generated from",
    "Treat `$ARGUMENTS` as the user's request",
    "Use the installed AI Berkshire Codex skill",
    "If the skill is not already loaded",
    "User arguments:",
)

REQUIRED_GENERATED_PHRASES = {
    "skill": (
        "## Codexアダプター注記",
        "同じ正本のワークフローを共有する",
        "`$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う",
    ),
    "prompt": (
        "AI Berkshireのスラッシュエントリ",
        "この依頼には、導入済みのAI Berkshire Codex Skill",
        "ユーザー引数：",
    ),
}

# 日本語の漢字と機械的に混同しにくい簡体字だけを対象にする。
# これは中国語判定器ではなく、未翻訳候補を絞り込むためのsignalである。
SIMPLIFIED_ONLY_CHARS = frozenset(
    "这发务业东报资负营现从并个后门见过还进远长买卖优觉图产种应为开关时场际仅须无总约证态专连选达问论经货币额润亏账录归护网"
)
CJK_RUN = re.compile(r"[\u3400-\u9fff]+")
INLINE_CODE = re.compile(r"`[^`]*`")
MARKDOWN_LINK_TARGET = re.compile(r"\]\([^)]*\)")
URL = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class AllowlistCategory:
    values: frozenset[str]
    scopes: frozenset[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*([^#\r\n]+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip('"\'')


def load_allowlist(path: Path = ALLOWLIST_PATH) -> dict[str, AllowlistCategory]:
    """依存ライブラリなしで、allowlistのvaluesとscopeだけを読む。"""
    categories: dict[str, dict[str, set[str]]] = {}
    current_category: str | None = None
    current_list: str | None = None

    for raw_line in _read(path).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        category_match = re.match(r"^  ([a-z0-9_]+):\s*$", raw_line)
        if category_match:
            current_category = category_match.group(1)
            categories[current_category] = {"values": set(), "scopes": set()}
            current_list = None
            continue

        if current_category is None:
            continue

        list_match = re.match(r"^    (values|scope):\s*$", raw_line)
        if list_match:
            current_list = "scopes" if list_match.group(1) == "scope" else "values"
            continue

        item_match = re.match(r"^      -\s+(.+?)\s*$", raw_line)
        if item_match and current_list:
            value = item_match.group(1).strip().strip('"\'')
            categories[current_category][current_list].add(value)
            continue

        if len(raw_line) - len(raw_line.lstrip()) <= 4:
            current_list = None

    return {
        name: AllowlistCategory(
            values=frozenset(parts["values"]),
            scopes=frozenset(parts["scopes"]),
        )
        for name, parts in categories.items()
    }


def find_untranslated_chinese(
    text: str,
    *,
    scope: str,
    allowlist: dict[str, AllowlistCategory] | None = None,
) -> list[str]:
    """簡体字signalを含み、指定scopeで許可されない語句を返す。"""
    allowlist = allowlist or load_allowlist()
    cleaned = INLINE_CODE.sub("", text)
    cleaned = MARKDOWN_LINK_TARGET.sub("]()", cleaned)
    cleaned = URL.sub("", cleaned)
    findings: list[str] = []

    for run in CJK_RUN.findall(cleaned):
        if not any(char in SIMPLIFIED_ONLY_CHARS for char in run):
            continue
        allowed = any(
            run in category.values and scope in category.scopes
            for category in allowlist.values()
        )
        if not allowed and run not in findings:
            findings.append(run)
    return findings


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"モジュールを読み込めない: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_config() -> list[Issue]:
    issues: list[Issue] = []
    if not CONFIG_PATH.is_file():
        return [Issue("config.missing", str(CONFIG_PATH.relative_to(ROOT)), "locale設定が存在しない")]

    text = _read(CONFIG_PATH)
    for key, expected in REQUIRED_CONFIG_VALUES.items():
        actual = _scalar(text, key)
        if actual != expected:
            issues.append(
                Issue(
                    "config.value",
                    str(CONFIG_PATH.relative_to(ROOT)),
                    f"{key}は{expected!r}である必要があるが、実値は{actual!r}である",
                )
            )

    for referenced in (ALLOWLIST_PATH, GLOSSARY_PATH):
        if not referenced.is_file():
            issues.append(
                Issue(
                    "config.reference",
                    str(CONFIG_PATH.relative_to(ROOT)),
                    f"参照先が存在しない: {referenced.relative_to(ROOT)}",
                )
            )
    return issues


def _canonical_names() -> set[str]:
    return {path.stem for path in CANONICAL_SKILLS.glob("*.md")}


def check_generated_artifacts() -> list[Issue]:
    issues: list[Issue] = []
    canonical = _canonical_names()
    generated_skill_names = {
        path.parent.name for path in CODEX_SKILLS.glob("*/SKILL.md") if path.parent.name not in CODEX_ONLY_SKILLS
    }
    prompt_names = {path.stem for path in CODEX_PROMPTS.glob("*.md")}

    if generated_skill_names != canonical:
        issues.append(
            Issue(
                "generated.skill_set",
                "codex-skills",
                f"正本との差分: missing={sorted(canonical - generated_skill_names)}, extra={sorted(generated_skill_names - canonical)}",
            )
        )
    if prompt_names != canonical:
        issues.append(
            Issue(
                "generated.prompt_set",
                "codex-prompts",
                f"正本との差分: missing={sorted(canonical - prompt_names)}, extra={sorted(prompt_names - canonical)}",
            )
        )

    for name in CODEX_ONLY_SKILLS:
        path = CODEX_SKILLS / name / "SKILL.md"
        if not path.is_file():
            issues.append(Issue("codex_only.missing", str(path.relative_to(ROOT)), "Codex専用Skillが存在しない"))
        if (CANONICAL_SKILLS / f"{name}.md").exists():
            issues.append(
                Issue(
                    "codex_only.conflict",
                    str(path.relative_to(ROOT)),
                    "同名の正本が存在し、自動生成対象と競合している",
                )
            )

    skill_sync = _load_module("localization_guard_sync_skills", SYNC_SKILLS)
    prompt_sync = _load_module("localization_guard_sync_prompts", SYNC_PROMPTS)

    for source in sorted(CANONICAL_SKILLS.glob("*.md")):
        name = source.stem
        source_text = _read(source)
        expected_skill = skill_sync.metadata_for(name, source.name, source_text) + skill_sync.codex_body(
            name, source.name, source_text
        )
        skill_path = CODEX_SKILLS / name / "SKILL.md"
        if skill_path.is_file() and _read(skill_path) != expected_skill:
            issues.append(
                Issue(
                    "generated.skill_content",
                    str(skill_path.relative_to(ROOT)),
                    f"{source.relative_to(ROOT)}からの生成結果と一致しない",
                )
            )

        prompt_path = CODEX_PROMPTS / source.name
        expected_prompt = prompt_sync.prompt_for(source)
        if prompt_path.is_file() and _read(prompt_path) != expected_prompt:
            issues.append(
                Issue(
                    "generated.prompt_content",
                    str(prompt_path.relative_to(ROOT)),
                    f"{source.relative_to(ROOT)}からの生成結果と一致しない",
                )
            )

    return issues


def check_generated_language() -> list[Issue]:
    issues: list[Issue] = []
    paths = [SYNC_SKILLS, SYNC_PROMPTS]
    paths.extend(sorted(CODEX_SKILLS.glob("*/SKILL.md")))
    paths.extend(sorted(CODEX_PROMPTS.glob("*.md")))

    for path in paths:
        text = _read(path)
        for phrase in DISALLOWED_GENERATED_PHRASES:
            if phrase in text:
                issues.append(
                    Issue(
                        "language.untranslated_wrapper",
                        str(path.relative_to(ROOT)),
                        f"生成経路に英語の利用者向け定型文が残っている: {phrase}",
                    )
                )

    for path in sorted(CODEX_SKILLS.glob("*/SKILL.md")):
        if path.parent.name in CODEX_ONLY_SKILLS:
            continue
        text = _read(path)
        for phrase in REQUIRED_GENERATED_PHRASES["skill"]:
            if phrase not in text:
                issues.append(
                    Issue(
                        "language.skill_wrapper",
                        str(path.relative_to(ROOT)),
                        f"日本語adapter定型文が不足している: {phrase}",
                    )
                )

    for path in sorted(CODEX_PROMPTS.glob("*.md")):
        text = _read(path)
        for phrase in REQUIRED_GENERATED_PHRASES["prompt"]:
            if phrase not in text:
                issues.append(
                    Issue(
                        "language.prompt_wrapper",
                        str(path.relative_to(ROOT)),
                        f"日本語prompt定型文が不足している: {phrase}",
                    )
                )
    return issues


def check_allowlist_contract() -> list[Issue]:
    issues: list[Issue] = []
    try:
        allowlist = load_allowlist()
    except (OSError, ValueError) as exc:
        return [
            Issue(
                "allowlist.read",
                str(ALLOWLIST_PATH.relative_to(ROOT)),
                f"allowlistを読めない: {exc}",
            )
        ]

    required_categories = {
        "formal_company_names",
        "external_api_values",
        "chinese_search_terms",
        "original_quotes",
        "source_titles",
        "legacy_report_parser_tokens",
    }
    missing = required_categories - set(allowlist)
    if missing:
        issues.append(
            Issue(
                "allowlist.categories",
                str(ALLOWLIST_PATH.relative_to(ROOT)),
                f"必須categoryが不足している: {sorted(missing)}",
            )
        )

    if not find_untranslated_chinese("検索語：财报", scope="user_facing_output", allowlist=allowlist):
        issues.append(
            Issue(
                "allowlist.scope",
                str(ALLOWLIST_PATH.relative_to(ROOT)),
                "検索用の中国語が一般の利用者向け本文でも無条件に許可されている",
            )
        )
    if find_untranslated_chinese("财报", scope="search_queries", allowlist=allowlist):
        issues.append(
            Issue(
                "allowlist.search",
                str(ALLOWLIST_PATH.relative_to(ROOT)),
                "許可済みの中国語検索語がsearch_queriesで拒否されている",
            )
        )
    if find_untranslated_chinese("企業価値、経営陣、財務状況を確認する。", scope="user_facing_output", allowlist=allowlist):
        issues.append(
            Issue(
                "allowlist.japanese",
                str(ALLOWLIST_PATH.relative_to(ROOT)),
                "日本語の漢字を未翻訳中国語として誤検出している",
            )
        )
    return issues


def run_checks() -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(check_config())
    issues.extend(check_allowlist_contract())
    issues.extend(check_generated_artifacts())
    issues.extend(check_generated_language())
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Berkshire日本語版のlocale契約を検査する")
    parser.add_argument("--json", action="store_true", help="結果をJSONで出力する")
    args = parser.parse_args(argv)

    issues = run_checks()
    payload = {
        "status": "pass" if not issues else "fail",
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif issues:
        print(f"日本語化品質ゲート: 不合格（{len(issues)}件）")
        for issue in issues:
            print(f"- [{issue.code}] {issue.path}: {issue.message}")
    else:
        print("日本語化品質ゲート: 合格")
        print("- locale設定、許可原語、正本と生成物、日本語定型文を確認した。")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
