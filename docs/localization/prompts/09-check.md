# Phase 9：残存中国語検査と最終統合検証

最初に`docs/localization/prompts/common.md`を読む。

```text
PHASE=Phase 9
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
```

## 目的

日本語化integration branch全体について、出力言語、正本と生成物、文書リンク、監査処理、manifest、path mapを最終確認する。

## 確認項目

- 全追跡ファイルの残存表現
- 正本と生成物の一致
- Markdownリンク
- 監査処理の日本語・中国語互換
- 数値、通貨、単位
- report manifestとpath mapの未完了項目

## 実行

```bash
python3 scripts/sync-codex-skills.py
python3 scripts/sync-codex-prompts.py
python3 -m compileall scripts tools
```

関連するfocused testを実行し、同期スクリプトの再実行で意図しない差分が出ないことを確認する。

## 代表監査

日本株、中国A株、香港株、米国株、業界調査、未上場企業、複数通貨の代表レポートを選び、`report_audit.py`のdry-runを実行する。

## 最終文書

- `docs/localization/final-report.md`
- `docs/localization/state.json`

最終SHA、日本語化済みファイル数、改名済みパス数、例外件数、blockedファイル、テスト結果、監査結果、未解決事項を記録する。`main`への統合、push、Pull Requestは行わない。

## Commit

コミットメッセージは「日本語化の最終検証を追加」とする。1コミット作成後、integration branchへff-only統合する。

## Oracle最終レビュー

統合後の実SHAを指定し、新規チャットで独立静的レビューを依頼する。編集やテスト実行は依頼しない。出力言語、生成物整合、共通指示、監査互換性、数値・通貨・単位、リンク、例外設定、manifestを確認対象とする。具体的な重大欠陥だけを報告し、欠陥がなければその旨を明示するよう依頼する。

送信失敗時は成功と報告せず、送信予定プロンプト全文を最終報告へ含める。
