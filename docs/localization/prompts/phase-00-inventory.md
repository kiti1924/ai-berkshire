# Phase 0：基準状態と日本語化対象インベントリ

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 0
WORK_BRANCH=chore/ja-l10n-baseline
REQUIRED_BASE_SHA=040f4baf989b37bcb6fa757ade6c8097f7c761f2
NEXT_PHASE_FILE=docs/localization/prompts/phase-01-locale-config.md
```

## 目的

日本語化開始時点のGit状態と中国語残存箇所を再現可能な形で記録する。このPhaseでは翻訳を行わない。

## 開始条件

- `main`、`origin/main`、`REQUIRED_BASE_SHA`の関係を確認する。
- `REQUIRED_BASE_SHA`がローカルに存在することを確認する。
- working treeがcleanであることを確認する。
- `integration/japanese-localization`が存在しない場合、`REQUIRED_BASE_SHA`から作成する。
- integration branchが存在する場合、異なる履歴を勝手に変更しない。

## 作成するファイル

- `docs/localization/inventory.md`
- `docs/localization/state.json`

## inventory.mdの必須内容

- 調査日
- `main`、`origin/main`、`upstream/main`の実SHA
- 総追跡ファイル数
- 中国語または簡体字を含むファイル数
- ディレクトリ別件数
- `skills`、`codex-skills`、`codex-prompts`、`tools`、`reports`、`docs`の区分
- 正本、自動生成物、Codex専用ファイル、既存成果物の区別
- 明示的に中国語出力を要求しているファイルと行
- 後方互換性のため残す必要がある中国語トークンの分類
- 現段階で確認できなかった事項

単純な漢字検出は日本語も拾うため、検出方法と限界を明記する。件数は可能な範囲で複数の方法により照合する。

## state.jsonの必須キー

- `chain_id`
- `initial_base_sha`
- `integration_branch`
- `current_phase`
- `current_integration_sha`
- `canonical_skill_count`
- `generated_skill_count`
- `generated_prompt_count`
- `tool_file_count`
- `legacy_content_file_count`
- `remaining_phase`
- `updated_at`

値は実際のGit状態と実測件数から取得し、推測しない。

## 禁止事項

- README、Skill、ツール、レポート本文を翻訳しない。
- 中国語ファイル名を変更しない。
- 自動生成物を再生成しない。
- 上流変更を取り込まない。

## 検証

- inventoryの件数を再計算して照合する。
- `state.json`をPythonで読み込み、JSON構文を確認する。
- `common.md`のGit差分確認を実行する。

## Commit

```text
日本語化対象の基準一覧を追加
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`phase-01-locale-config.md`を指定するOracle引継ぎプロンプトを送信する。次Phaseの`REQUIRED_BASE_SHA`には、Phase 0統合後の実SHAを使用する。
