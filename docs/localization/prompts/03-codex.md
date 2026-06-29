# Phase 3：Codex SkillとPromptの再生成

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 3
WORK_BRANCH=fix/ja-codex-sync
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/04-audit.md
```

## 目的

日本語化した`skills/*.md`からCodex用SkillとPromptを正規の同期処理で再生成し、Claude CodeとCodexの整合を回復する。

## 実行

```bash
python3 scripts/sync-codex-skills.py
python3 scripts/sync-codex-prompts.py
```

## Codex専用Skill

次は自動生成対象外の手書きSkillである。

```text
codex-skills/investment-memo-craft/SKILL.md
```

このファイルに残る中国語の見出し、ファイル名例、出力テンプレートを自然な日本語へ変更する。Skill名、frontmatter、Codex専用であるという性質は維持する。

特に次の種別を確認する。

- 核心データの一覧
- 事業の本質
- 経済的な堀
- リスク一覧
- 経営陣評価
- 業界と長期潮流
- バリュエーションと安全余裕
- 最終判断と行動一覧
- AI分析の信頼度と投資判断の確度
- データ出典と監査記録

## 検証

- Codex Skill 18件が`skills/*.md`から生成されている。
- Codex Prompt 18件が生成されている。
- Codex専用Skillが上書きされていない。
- `$ARGUMENTS`が保持されている。
- frontmatterが有効である。
- 参照先が正しい。
- 中国語出力固定が残っていない。
- 同期スクリプトを2回目に実行して差分が発生しない。

再度実行する。

```bash
python3 scripts/sync-codex-skills.py
python3 scripts/sync-codex-prompts.py
```

その後、`common.md`のGit差分確認を実行する。

## 禁止事項

- 生成対象の`codex-skills`を個別手修正しない。
- `skills/*.md`をこのPhaseで追加修正しない。
- reportsを変更しない。
- 同期結果の大量差分を未確認のままcommitしない。

## Commit

```text
Codex Skillへ日本語化を反映
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`04-audit.md`を指定するOracle引継ぎプロンプトを送信する。
