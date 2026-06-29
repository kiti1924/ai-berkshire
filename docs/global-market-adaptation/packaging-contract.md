# Global Market Adaptation Packaging Contract Specification

- 文書ID: `ABG-PACKAGING-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、トップレベルの利用者向けSkill（`skills/*.md`）と、内部参照資料（市場別仕様、共通契約、投資家レンズ）のパッケージング・配布分離構造を定義する。

## 2. ディレクトリ構成

### 2.1 Canonical Source (Repository Layout)
```text
skills/
  investment-research.md   # 利用者向けエントリーポイント
  investment-team.md
  earnings-review.md
  quality-screen.md

  shared/                  # 内部参照資料 (コマンド一覧へ非露出)
    agent-contract.md
    data-contract.md

  markets/                 # 市場別内部参照資料
    us.md
    jp.md
    cn-sh-a.md
    hk.md

  lenses/                  # 投資家レンズ内部参照資料
    governance-allocator.md
    management-organization.md
```

### 2.2 配布分離ルール
- トップレベルの `skills/*.md` のみが Claude Code commands / Codex skills の主コマンドとして導入される。
- `shared/`, `markets/`, `lenses/` などの内部参照資料は、Claude Code環境では `AI_BERKSHIRE_HOME/references/` へ、Codex環境では各Skillパッケージ直下の `references/` ディレクトリへ同梱される。
