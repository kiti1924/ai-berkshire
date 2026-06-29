# Phase 1：共通日本語設定とプロジェクト指示

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 1
WORK_BRANCH=feat/ja-locale-config
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/02-skills.md
```

## 目的

Claude CodeとCodexに共通する日本語出力方針を正本化する。日本語を各Skillへ重複して埋め込まず、多言語対応を維持できる共通設定を作る。

## 対象

- `config/localization.yaml`
- `AGENTS.md`
- `CLAUDE.md`
- `ai_CLAUDE.md`
- `docs/localization/glossary.md`
- `docs/localization/chinese-allowlist.yaml`
- `docs/localization/state.json`

## 共通設定

`config/localization.yaml`に少なくとも次を定義する。

```yaml
output_language: ja
locale: ja-JP
timezone: Asia/Tokyo
writing_style: da-dearu
```

必要に応じて、結論先行、事実と推定の区別、通貨・単位・基準日の明記、原文識別子の保持方針も構造化する。

## プロジェクト指示

`AGENTS.md`と`CLAUDE.md`へ次を反映する。

- ユーザー向け出力は原則日本語
- 文体は「だ・である調」
- 結論を先に示す
- 事実、企業説明、市場予想、計算推定、仮定、評価を区別する
- 通貨、単位、基準日、会計期間、会計基準を明記する
- 中国語情報源を検索しても最終出力は日本語にする
- ファイル名、関数名、コマンド、API名、JSONキーは必要に応じて原文を維持する
- upstream、作業リポジトリ、ローカルパス、default branchの正しい関係
- push、Pull Request、`main`変更は明示依頼時のみ
- `skills/*.md`が正本であり、変更後に同期処理が必要であること

`ai_CLAUDE.md`は日本語版の保守に必要な内容へ整理する。

## 用語集

`glossary.md`には中国語、英語、日本語、使用上の注意を記録する。少なくとも次を扱う。

`财报`、`护城河`、`估值`、`管理层`、`归母净利润`、`股本`、`港股`、`A股`、`公众号`、`雪球`、`亿元`、`万亿`、`巴菲特`、`芒格`、`段永平`、`李录`

## 許可リスト

`chinese-allowlist.yaml`には、後方互換性のため許可する中国語を次の分類で記録する。

- 企業の正式名称
- 外部API値
- 中国語検索語
- 原文引用
- 出典タイトル
- 旧レポート解析用トークン

許可理由と適用範囲を記載し、過度に広いパターンを避ける。

## 禁止事項

- `skills/*.md`を変更しない。
- `codex-skills`と`codex-prompts`を変更しない。
- `tools`を変更しない。
- READMEを変更しない。
- `reports`、`筛选公司`、`实盘记录`を変更しない。

## 検証

- YAML構文を確認する。
- Markdown内リンクを確認する。
- リポジトリURLとローカルパスを確認する。
- 旧上流リポジトリを作業先として扱う記述が残っていないことを確認する。
- `common.md`のGit差分確認を実行する。

## Commit

```text
日本語出力の共通設定を追加
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`02-skills.md`を指定するOracle引継ぎプロンプトを送信する。
