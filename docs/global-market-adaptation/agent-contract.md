# Global Market Adaptation Agent Contract Specification

- 文書ID: `ABG-AGENT-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、標準4 Agentおよび日本市場向け深掘り2 Agentの責務、入出力契約、および分析方法論の統合ルールを定義する。

## 2. Agent一覧と責務

### 2.1 標準4 Agent (`Agent ID`)

| Agent ID | 責務 | 基礎方法論 | 日本市場での追加方法論 |
|---|---|---|---|
| `business_quality` | 顧客価値、事業本質、モート、経営者・組織定性 | 段永平型 | 藤野英人型（経営者・組織・人的資本） |
| `financial_capital` | 財務品質、内在価値、資本配分、ガバナンス | バフェット型 | 村上世彰型（資本配分・ガバナンス・価値解放） |
| `competition_risk` | 競争、失敗経路、反証条件、リスク | マンガー型 | 日本特有組織硬直・承継・少数株主リスク |
| `structural_change` | 長期需要、技術革新、政策、産業構造 | 李録型 | 人口動態、産業再編、東証資本市場改革 |

*注: 日本語文書、Prompt、Skill、レポートでは「モート」を標準用語とする。「護城河」を新規追加・使用してはならない。*

### 2.2 深掘りAgent (`Deep-Dive Agents`)

| Agent ID | 責務 | 方法論由来 | 起動条件例 |
|---|---|---|---|
| `governance_allocator` | 余剰資本、政策保有株、親子上場、触媒 | 村上世彰型 | 親子上場、過剰現金、アクティビスト対象、PBR低迷 |
| `management_organization` | 経営者評価、企業文化、人的資本、後継者 | 藤野英人型 | オーナー経営中小型、後継者問題、経営者依存高 |

## 3. 入出力データ契約

### 3.1 共通入力
全Agentは同一の `FactSnapshot` および選択された `Document` リストを参照する。各Agentが独自にWeb検索で重用財務データを個別再取得することは禁止される。

### 3.2 Agent標準出力契約 (JSON / Struct)
```json
{
  "agent_id": "business_quality",
  "conclusion": "string",
  "score": 0.0,
  "confidence": "high",
  "claims": ["string"],
  "evidence_ids": ["string"],
  "fact_ids": ["string"],
  "risks": ["string"],
  "falsifiers": ["string"],
  "unknowns": ["string"],
  "warnings": ["string"]
}
```
