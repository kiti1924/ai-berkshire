# Phase 6：日本語化の総合検証

最初に`docs/localization/prompts/common.md`を読む。

```text
PHASE=Phase 6
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/07-reports.md
```

## 目的

新規出力経路が日本語となり、正本と生成物が一致し、日本語レポートを監査できることを自動確認する。

## 作成候補

必要に応じて次を追加する。

- `tests/test_localization_contracts.py`
- `tests/test_report_audit_locales.py`
- `tests/fixtures/report_ja.md`
- `tools/localization_guard.py`
- `docs/localization/state.json`

## 検査条件

- 日本語出力設定を確認する。
- 正本と生成物の一致を確認する。
- 許可された原語と未翻訳文言を区別する。
- 数値、URL、リンク、識別子を確認する。
- 漢字の存在だけをエラー条件にしない。

## Commit

コミットメッセージは「日本語化の契約テストを追加」とする。
