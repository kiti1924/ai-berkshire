# Phase 4：ツール出力と監査処理の日本語化

最初に`docs/localization/prompts/common.md`を読み、本ファイルをPhase固有の完全な実行指示として扱う。

```text
PHASE=Phase 4
WORK_BRANCH=feat/ja-tool-output
REQUIRED_BASE_SHA=<Oracleから渡された実SHA>
NEXT_PHASE_FILE=docs/localization/prompts/05-docs.md
```

## 目的

ツールの利用者向け表示、CLIヘルプ、エラー、監査結果を日本語化する。中国語レポートや中国APIとの後方互換性は維持する。

## 対象

- `tools/ashare_data.py`
- `tools/financial_rigor.py`
- `tools/log-command.sh`
- `tools/momentum_backtest.py`
- `tools/momentum_backtest_v2.py`
- `tools/morningstar_fair_value.py`
- `tools/report_audit.py`
- `tools/stock_screener.py`
- `tools/xueqiu_scraper.py`

必要なfocused testを`tests/`へ追加してよい。

## 利用者向け表示

次を自然な日本語へ変更する。

- print出力
- CLI descriptionとhelp
- 警告とエラー
- 成功判定
- 表見出し
- シナリオ名
- 監査結果
- 中国語コメントとdocstring

外部仕様の原語、APIフィールド値、正式名称は必要に応じて保持する。

## report_audit.py

日本語レポートと旧中国語レポートの両方を解析できるようにする。少なくとも次を両対応にする。

| 中国語 | 日本語 |
|---|---|
| 来源 | 出典 |
| 说明 | 説明 |
| 备注 | 注記 |
| 数据来源 | データ出典 |
| 亿元 | 億元 |
| 万亿 | 兆 |

注意事項：

- `亿元`を「億円」と解釈しない。
- CNY、HKD、JPY、USDを区別する。
- 中国語単位の既存抽出能力を削除しない。
- 日本語の「億円」「億ドル」「億香港ドル」等を適切に扱う。
- 数値抽出の過検出を増やさない。

## 内部互換性

次は内部互換性のため残してよい。

- 中国APIのフィールド値
- 中国語検索キーワード
- 中国企業の正式名称
- 外部サービス名
- APIレスポンスの原文
- 旧レポート解析用トークン

利用者向け表示との境界を明確にする。

## 禁止事項

- 外部APIへ実通信しない。
- データ取得仕様を無関係に変更しない。
- 財務計算式を変更しない。
- floatとDecimalの扱いを無関係に変更しない。
- 既存中国語レポート対応を削除しない。
- reportsを変更しない。

## 検証

最低限、次を実行する。

```bash
python3 -m compileall scripts tools
```

focused testで少なくとも次を検証する。

- 日本語CLIヘルプ
- 日本語エラー
- 日本語単位の抽出
- 中国語後方互換
- 通貨誤認防止
- 数値、URL、JSON出力の互換性

最後に`common.md`のGit差分確認を実行する。

## Commit

```text
財務ツールと監査出力を日本語化
```

1コミット作成後、integration branchへff-only統合する。

## 次Phase

統合成功後、`05-docs.md`を指定するOracle引継ぎプロンプトを送信する。
