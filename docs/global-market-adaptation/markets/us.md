# US Market Adaptation Specification

- 文書ID: `ABG-MARKET-US-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、米国（US）市場を対象とする `USMarketAdapter` のデータ取得経路、対象書類、および固有分析論点を定義する。

## 2. データ取得経路

- **主要正本**: SEC EDGAR (Company Submissions API, XBRL), 会社公式IR
- **対象書類**: Form 10-K, 10-Q, 8-K, DEF 14A (Proxy Statement), Form 4, Schedule 13D/13G, Form 20-F, 6-K
- **二次情報**: Yahoo Finance, StockAnalysis, Macrotrends, 金融報道

## 3. 米国固有チェック項目

1. Stock-Based Compensation (SBC) の規模と希薄化影響
2. 自社株買いの純効果 (Buyback net of dilution)
3. GAAP vs Non-GAAP 調整項目の妥当性
4. のれん (Goodwill) および M&A 減損リスク
5. 議決権割当構造 (Dual-class voting) および創業者支配権
