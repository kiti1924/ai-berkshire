# Phase 2：正本ワークフロー18件の日本語化

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 2
WORK_BRANCH=feat/ja-canonical-skills
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/03-codex.md
```

## 目的

Claude CodeとCodexの共通ワークフロー正本である`skills/*.md`を、自然な日本語へ変更する。

## 対象

`skills/`直下にある次の18ファイルだけを正本として編集する。

- `bottleneck-hunter.md`
- `deep-company-series.md`
- `dyp-ask.md`
- `earnings-review.md`
- `earnings-team.md`
- `financial-data.md`
- `industry-funnel.md`
- `industry-research.md`
- `investment-checklist.md`
- `investment-research.md`
- `investment-team.md`
- `management-deep-dive.md`
- `news-pulse.md`
- `portfolio-review.md`
- `private-company-research.md`
- `quality-screen.md`
- `thesis-tracker.md`
- `wechat-article.md`

## 日本語化方針

単語置換ではなく、自然な日本語として再構成する。

- 中国語の語順をそのまま持ち込まない。
- 日本の投資調査で通用する用語を使う。
- 文体は「だ・である調」とする。
- 結論を先に示す。
- 事実、推定、仮定、評価を区別する。
- 中国語出力を固定する指定を除去する。
- 共通言語設定を参照し、最終出力を日本語にする。
- 中国語資料を検索対象から除外しない。
- 中国語検索語は検索用であることを明示する。
- 中国企業・人物の正式名称は必要に応じて原名を併記する。
- `公众号`は文脈に応じて「WeChat公式アカウント記事」とする。
- `投资论文`は文脈に応じて「投資仮説」等へ変更する。
- 財務用語は`docs/localization/glossary.md`へ合わせる。

## 保持するもの

- ファイル名
- `$ARGUMENTS`
- コマンド名
- 関数名
- JSONキー
- API名
- ツール名
- URL
- コードブロック内の実行コマンド
- 数式
- 入出力スキーマ
- 外部サービスの正式名称
- 検索に必要な原語キーワード

## 禁止事項

- `codex-skills`を直接編集しない。
- `codex-prompts`を直接編集しない。
- 同期スクリプトを実行しない。
- `tools`、README、reportsを変更しない。
- 内容を短縮して機能要件を失わせない。
- 財務計算や監査要件を弱めない。

## 検証

18ファイルすべてについて次を確認する。

- frontmatter
- `$ARGUMENTS`
- 相対パス
- コードフェンス
- JSON例
- Claude Code固有のAgent、Task、WebSearch等の意味
- 出力テンプレート
- 財務監査手順
- 中国語出力を強制する文言が残っていないこと
- 簡体字の残存が許可リスト対象であること

`common.md`のGit差分確認を実行する。

## Commit

```text
投資調査Skillを日本語化
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`03-codex.md`を指定するOracle引継ぎプロンプトを送信する。
