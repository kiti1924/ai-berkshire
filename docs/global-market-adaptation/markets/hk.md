# Hong Kong Market Adaptation Specification

- 文書ID: `ABG-MARKET-HK-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、香港証券取引所（HK）市場を対象とする `HongKongMarketAdapter` のデータ取得経路、対象書類、および固有分析論点を定義する。

## 2. データ取得経路

- **主要正本**: HKEXnews (年次報告, 中間報告, 適時公告, 持分開示), 会社公式IR
- **二次情報**: Yahoo Finance, AASTOCKS, 報道機関

## 3. 香港市場固有チェック項目

1. 銘柄コードの leading zero 保持 (例: `0700.HK`)
2. 支配株主の持分割合および少数株主保護
3. 接続取引 (Connected transactions)
4. 第三者割当 (Placements) による株式希薄化リスク
5. H株, レッドチップ, Pチップ等の企業形態識別および大陸露出度 (Mainland exposure)
