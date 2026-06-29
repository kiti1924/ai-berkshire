# Global Market Adaptation Goal Specification

- 文書ID: `ABG-GOAL-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 実装指示: `tasks/global_market_adaptation/README.md` (`ABG-GOAL-INSTRUCTIONS`)
- 状態: Active

## 1. 概要

本仕様書は、Global Market Adaptation プロジェクトの14のGoal（Goal 0 〜 Goal 13）に関する全体依存構造、成果物、および自動品質ゲートの判定契約を定義する。

## 2. Goal依存関係概要

```text
Goal 0 (Foundation)
 ├── Goal 1 (Installation)
 └── Goal 2 (Data Contracts)
      ├── Goal 3 (Security Resolution)
      ├── Goal 4 (Access Policy)
      └── Goal 5 (Fact Snapshot & Validation)
           ├── Goal 6 (US Adapter)
           ├── Goal 7 (JP Adapter)
           ├── Goal 8 (Shanghai A Adapter)
           └── Goal 9 (Hong Kong Adapter)
                └── Goal 10 (Agent Methodology)
                     └── Goal 11 (Skill & Workflow Integration)
                          └── Goal 12 (Reports & Degraded Ops)
                               └── Goal 13 (End-to-End Acceptance)
```

## 3. 全Goal状態一覧

すべてのGoal状態は `tasks/global_market_adaptation/queue.json` および `tasks/global_market_adaptation/queue.md` で完全同期・管理される。
