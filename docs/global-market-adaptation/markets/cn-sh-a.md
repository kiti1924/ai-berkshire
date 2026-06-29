# Shanghai A Market Adaptation Specification

- 文書ID: `ABG-MARKET-CN-SH-A-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、上海証券取引所A株（CN_SH_A）市場を対象とする `ShanghaiAMarketAdapter` のデータ取得経路、対象書類、および固有分析論点を定義する。

## 2. データ取得経路

- **主要正本**: 上海証券取引所 (SSE) 公告・法定定期報告, 会社公式IR
- **二次情報**: Yahoo Finance, 東方財富 (Eastmoney), 報道機関

## 3. 上海A株固有チェック項目

1. 国有企業 (SOE) vs 民営企業区分、および最終実質支配者 (Ultimate Controller)
2. 関連当事者取引 (Related-party transactions) の規模と妥当性
3. 大株主の株式質権設定 (Share pledges) リスク
4. 政府補助金 (Government subsidies) および非経常損益依存度
5. 売掛金・棚卸資産の滞留および大株主の資金占用リスク
