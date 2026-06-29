# Global Market Adaptation Security Resolution Specification

- 文書ID: `ABG-SECURITY-RESOLUTION-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、利用者が入力した企業名、Ticker、証券コードから対象市場（US, JP, CN_SH_A, HK）および単一の対象証券（Security）を解決する `SecurityResolver` および `MarketRouter` の契約を定義する。

## 2. 判定・ルーター規則

### 2.1 4市場識別パターン

| 入力パターン例 | 判別市場 (`market_id`) | 備考 |
|---|---|---|
| `AAPL`, `MSFT`, `NVDA` | `US` | 米国アルファベットTicker |
| `7203`, `7203.T`, `トヨタ自動車` | `JP` | 4桁数字（または.T suffix）、日本企業名 |
| `600519`, `600519.SS`, `貴州茅台` | `CN_SH_A` | 上海A株 6桁（60/688等）または.SS suffix |
| `0700.HK`, `0700`, `700`, `騰訊` | `HK` | 4〜5桁.HK suffix、または leading zero補正コード |

### 2.2 ADRおよびクロスリスティングの扱い

- ADR（例: 米国上場のBABA）と原株（香港上場の9988.HK）は同一発行体（`issuer_id`）であっても、別の `security_id` として明確に分離する。
- 市場は発行会社の国籍ではなく、分析対象証券の上場市場で決定する。

### 2.3 対象外証券 (Out of Scope) 判定

初期実装では以下の証券種別を判定し、通常企業評価を行わずに `out_of_scope` を返す。
- ETF, ETN, REIT, 優先株, 債券, オプション, 先物, SPAC, 銀行, 保険, 証券会社
