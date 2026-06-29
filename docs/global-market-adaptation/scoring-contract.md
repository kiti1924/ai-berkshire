# Global Market Adaptation Scoring Contract Specification

- 文書ID: `ABG-SCORING-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、投資研究評価における各Agentのスコアリング基準、重み付け統合、および信頼度（confidence）の算出契約を定義する。

## 2. スコアリング体系

- **スケール**: 0.0 〜 10.0 （小数点第1位まで表記）
- **判定閾値**:
  - `8.5 - 10.0`: 極めて優秀 (Tier 1)
  - `7.0 - 8.4`: 優秀 (Tier 2)
  - `5.0 - 6.9`: 中立 / 要観察 (Tier 3)
  - `0.0 - 4.9`: 高リスク / 不適格 (Tier 4)

## 3. 市場別重み付け調整 (Overlay)

| 市場 (`market_id`) | `business_quality` | `financial_capital` | `competition_risk` | `structural_change` |
|---|---|---|---|---|
| `US` | 35% | 30% | 20% | 15% |
| `JP` | 30% | 35% | 20% | 15% |
| `CN_SH_A` | 30% | 25% | 25% | 20% |
| `HK` | 25% | 35% | 25% | 15% |

※ `JP`市場では村上世彰型・藤野英人型レンズが組み込まれた `financial_capital` および `business_quality` の比率を重視する。
