# Phase 5：README・文書・図表の日本語化

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 5
WORK_BRANCH=docs/ja-documentation
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/quality-gate.md
```

## 目的

日本語版リポジトリの公開文書、導入手順、図表を日本語環境へ整合させる。

## 対象

- `README.md`
- `README_EN.md`
- `docs/ROADMAP.md`
- `docs/`配下の非レポート文書
- `assets/architecture.mmd`
- `assets/architecture.png`
- `.gitignore`内の中国語コメント
- `docs/localization/state.json`

このPhaseでは`reports`、`筛选公司`、`实盘记录`、ルート直下の投資レポートを変更しない。

## README.md

- 日本語を主言語にする。
- 先頭を`日本語 | English`にする。
- 自然な日本語で説明する。
- clone先を`kiti1924/ai-berkshire-JP`にする。
- upstreamとの関係を明記する。
- Claude CodeとCodexの正本・生成物関係を説明する。
- 日本語の使用例を掲載する。
- 日本語出力設定を説明する。
- 投資助言ではないことを明記する。
- 既存の実績数値を変更しない。
- 数値の基準期間を維持する。
- 存在しない機能を追加しない。

## README_EN.md

英語本文は日本語化しない。次だけを修正する。

- 日本語版READMEへの表記
- 変更されたリンク
- リポジトリURL
- 中国語版を前提とした説明
- 存在しないパス

## 図表

`assets/architecture.mmd`の中国語ラベルを日本語へ変更する。

`architecture.png`は次の優先順で扱う。

1. リポジトリ内または既存環境の正式な生成方法で再生成する。
2. 依存追加なしで生成できない場合、READMEをGitHub Mermaid表示へ変更する。
3. 古い中国語PNGが参照されなくなった場合、生成物として安全に削除する。

新しい依存関係を無断でダウンロードしない。

## 禁止事項

- reportsの本文を変更しない。
- 過去レポートのファイル名を変更しない。
- READMEの数値を根拠なく修正しない。
- 画像を手作業で偽造しない。
- 上流READMEの構成を必要以上に破壊しない。

## 検証

- Markdownリンク
- 画像・Mermaid参照
- clone URL
- Skill数
- コマンド例
- 日本語版と英語版の相互リンク
- `common.md`のGit差分確認

## Commit

```text
READMEと公開文書を日本語化
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`quality-gate.md`を指定するOracle引継ぎプロンプトを送信する。
