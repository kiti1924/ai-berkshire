# Global Market Adaptation Report Contract Specification

- 文書ID: `ABG-REPORT-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、調査・分析結果の保存パス、レポート標準フォーマット、マニフェスト、および劣化動作（degraded operation）時の表示契約を定義する。

## 2. 出力パス構造

### 2.1 標準出力パス (Standard Output)
```text
reports/{market_id}/{ticker}-{issuer_slug}/{YYYYMMDD}-{skill}.md
```

### 2.2 詳細出力ディレクトリ (Detailed Artifact Bundle)
```text
reports/{market_id}/{ticker}-{issuer_slug}/{run_id}/
  report.md
  facts.json
  evidence.json
  documents.json
  run-manifest.json
```

## 3. レポート必須記載項目

すべての生成レポートは以下のメタデータおよび章構成を含まなければならない。

1. **メタデータブロック**:
   - 対象証券 (`security_id`, `ticker`, `legal_name`)
   - 上場市場 (`market_id`)
   - 分析時点 (`as_of`)
   - 株価・評価時点
   - 使用通貨 (`trading_currency`, `reporting_currency`)
   - 会計基準 (`accounting_standard`)
   - 実行ステータス (`completed` | `partial` | `failed`)
2. **主要出典リスト (Primary Sources)**
3. **データ不足・警告事項 (Data Gaps / Warnings)**
4. **Agent分析結果統合 (Integrated Analysis)**
5. **反証条件 (Falsifiers)**
6. **AI分析信頼度 (Confidence) & 免責事項 (Disclaimer)**

## 4. 秘密情報遮断ルール (Secret Redaction)

APIキー（`EDINET_API_KEY`等）、Cookie、Authorizationヘッダー、ローカル絶対パス中のユーザー名は、レポートおよびJSON成果物へ一切出力してはならない。
