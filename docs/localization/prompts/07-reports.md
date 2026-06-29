# Phase 7：既存レポート本文のバッチ日本語化

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 7
BATCH_ID=<Oracleから渡された実バッチ番号>
WORK_BRANCH=docs/ja-reports-batch-<BATCH_ID>
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
MAX_FILES=25
MAX_SOURCE_CHARACTERS=120000
```

## 目的

既存中国語レポートの本文を、数値、通貨、日付、出典、判断を変えずに日本語化する。一度に全件を処理せず、決定的な順序で安全にバッチ処理する。

## 対象

- `reports/`
- `筛选公司/`
- `实盘记录/`
- `RKLB-investment-research.md`
- `sailis-touzi-yanjiu-baogao.md`
- インベントリで既存投資成果物に分類されたルートファイル

このPhaseではファイル名とディレクトリ名を変更しない。

## Manifest

`docs/localization/report-manifest.json`を使用する。BATCH 001で存在しない場合は生成する。

各項目には少なくとも次を保持する。

- `path`
- `content_status`
- `original_blob_sha`
- `translated_blob_sha`
- `batch_id`
- `numeric_guard_status`
- `url_guard_status`
- `audit_status`
- `notes`

未処理ファイルをパス順に選び、`MAX_FILES`または`MAX_SOURCE_CHARACTERS`のいずれか早い方で止める。

## 日本語化要件

- 自然な日本語とする。
- 中国語語順を持ち込まない。
- 投資判断の強さを変更しない。
- 事実と意見の区別を維持する。
- 数値、日付、通貨、会計期間を変更しない。
- URL、ticker、ISIN、証券コードを変更しない。
- Markdown表、コードブロック、脚注を壊さない。
- 引用を翻訳した場合は日本語訳であることを明示する。
- 企業や人物の正式名称は必要に応じて原名を併記する。
- `亿元`を「億円」と誤訳しない。
- `万亿`は文脈と通貨を確認して「兆」へ表現する。
- 原文の誤りを勝手に修正せず、発見事項を`notes`へ記録する。

## 保全確認

翻訳前後で次を照合する。

- 数値トークンとパーセント
- 通貨コード
- URLとMarkdownリンク先
- ticker、ISIN、証券コード
- 日付と脚注番号

説明できない差異があるファイルはcommit対象に含めず、manifestへ`blocked`として記録する。

重要レポートは可能な範囲で次を実行する。

```bash
python3 tools/report_audit.py extract --report <対象> --dry-run
```

このPhaseでは外部情報を再調査せず、既存の事実関係を保持する。

## 禁止事項

- 機械的な一括置換だけで完了させない。
- 全レポートを一度に編集しない。
- ファイル名を変更しない。
- 数値や出典を翻訳都合で変更しない。
- 未処理ファイルを処理済みと記録しない。
- blockedファイルを無理にcommitしない。

## Commit

```text
既存レポートを日本語化 batch <BATCH_ID>
```

focused checkと`common.md`のGit差分確認後、1コミットを作成し、integration branchへff-only統合する。

## 次Phaseの分岐

未処理ファイルが残る場合は、`BATCH_ID`を1増やし、統合後SHAを使って同じ`07-reports.md`をOracleへ送信する。

全対象が完了または明示的にblockedとなった場合は、次を指定してPhase 8を送信する。

```text
NEXT_PHASE_FILE=docs/localization/prompts/08-paths.md
BATCH_ID=001
MAX_RENAMES=80
```

## 追加報告項目

- `PROCESSED_FILES`
- `BLOCKED_FILES`
- `NUMERIC_GUARD_RESULT`
- `URL_GUARD_RESULT`
- `AUDIT_RESULT`
- `MANIFEST_REMAINING`
