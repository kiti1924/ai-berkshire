---
name: dividend-screen
description: 高配当かつ価格下落株のスクリーニングを実行し、優良割安銘柄を抽出する
---

## Codexアダプター注記

このSkillは`skills/dividend-screen.md`から生成され、Claude CodeとCodexで同じ正本のワークフローを共有する。

- `$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う。
- 調査レポート等のファイル書き出し指示（例: `reports/{会社名}/...`）がある場合は、単に会話上にMarkdownを出力して終了せず、必ずファイル書き込みツールまたはシェルコマンド（`mkdir -p reports/{会社名}` および ファイル書き込み）を実行して実際にファイルとして保存すること。
- Claude Code固有の機能（Task, Agent等）は、このセッションで利用できる最も近いCodex機能（サブエージェント、Web検索、ローカルシェル等）へ置き換える。
- 共通ツールは本リポジトリの`tools/`（`python3 tools/...`）を使用し、`AGENTS.md`の調査品質規則（精密計算ツールでの検証、不確実性の明示等）を維持する。

# 高配当かつ価格下落株スクリーニングスキル

このスキルは、一時的な株価の下落によって配当利回り（配当比率）が高くなっている（5%など）魅力的な企業を自動で探し出し、評価するためのフローを定義したものである。

エージェント（Antigravity、Codex等）は、本スキルに従って自律的にスクリーニングと評価を実施する。

## 動作要件

*   Python 3.x
*   Yahoo Finance への接続環境（curl）
*   スクリプト：[dividend_screener.py](file:///d:/Documents/repos/ai-berkshire/tools/dividend_screener.py)

---

## 実行手順

### 手順1: 引数の解析としきい値の決定

指定されたパラメータを元に、しきい値を決定する。
ユーザーが何も指定しない場合のデフォルト値は以下とする。

*   **最小配当利回り (`--min-yield`)**: 4.0%
*   **52週高値からの最小下落率 (`--min-drop`)**: 15.0%

対象の銘柄（tickers）が指定されている場合はそれを優先し、指定がない場合は [watchlist.json](file:///d:/Documents/repos/ai-berkshire/data/watchlist.json) から全銘柄をロードして走査する。

### 手順2: スクリーナーの実行

以下のコマンドを使用してスクリーニングを実行する。

```bash
# デフォルト条件でウォッチリスト全体をスクリーニング
python3 tools/dividend_screener.py

# カスタム条件で特定の銘柄群をスクリーニングする例
python3 tools/dividend_screener.py --min-yield 5.0 --min-drop 20.0 T VZ IBM
```

### 手順3: 抽出結果の分析と報告

スクリーナーによって抽出された銘柄リストを確認し、以下を出力する。

1.  **適合銘柄の要約表**: チッカー、現在値、配当利回り、52週高値、下落率。
2.  **初期分析と推奨されるアクション**:
    *   抽出された銘柄の中から、特に配当の安全性やビジネスモデルの強固さ（Moatの有無）の観点で深掘りするべき優先銘柄を 1〜2 社ピックアップする。
    *   ピックアップした銘柄について、[investment-checklist.md](file:///d:/Documents/repos/ai-berkshire/skills/investment-checklist.md) スキルを適用して購入前評価を実施することを推奨する。

### 手順4: 財務精度のクロスチェック（オプション）

スクリーニングされた銘柄の財務データに疑義がある場合、または更なる精度検証を行う場合は、[financial_rigor.py](file:///d:/Documents/repos/ai-berkshire/tools/financial_rigor.py) を用いて以下のようにバリュエーションを精密に再検証する。

```bash
python3 tools/financial_rigor.py verify-valuation --price {株価} --dividend {1株当たり配当金}
```

---

## 注意事項

1.  **一時的下落の理由を調べること**:
    株価の下落が「一時的なもの（市場全体の調整、一時的な業績の振れ）」なのか、「構造的な衰退（ビジネスモデルの崩壊、減配リスクの高まり）」なのかを区別することが極めて重要である。
2.  **減配リスクの評価**:
    配当性向（Payout Ratio）やフリーキャッシュフロー（FCF）の推移を確認し、高配当が維持可能かを確認すること。
