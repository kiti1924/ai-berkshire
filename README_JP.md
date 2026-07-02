[中文](README.md) | [English](README_EN.md) | 日本語

# AI Berkshire — AI時代のバリュー投資リサーチ・フレームワーク

> "Price is what you pay, value is what you get." — Warren Buffett
>
> AIで投資リサーチの深さと速度を再定義する。

**AI Berkshire** は、Claude Code と Codex の両方で使える投資リサーチ用 Skill 群である。バフェット、マンガー、段永平、李録の4つの投資思考をワークフロー化し、AI Agent によってプロ水準の調査プロセスを再現する。

一人 + Claude Code / Codex = 自分専用の投資リサーチチーム。

---

## 実運用成績

> ペーパートレードではない。実資金ポートフォリオに基づく検証済みの運用実績である。

### 2024年通期リターン：+69.29%

<img src="assets/2024-returns.jpg" width="300" />

### 2025年年初来リターン：+66.38%

<img src="assets/2025-returns.jpg" width="300" />

### ベンチマーク比較

| 指標 | 2024年通期 | 2025年年初来 |
|------|------------|--------------|
| **本フレームワーク実運用** | **+69.29%** | **+66.38%** |
| ハンセン指数 | +17.67% | +27.77% |
| S&P 500 | +23.31% | +16.39% |
| CSI 300 | +14.68% | +17.66% |
| Nasdaq Composite | +28.64% | +20.36% |

**2024年の超過リターン**：S&P 500を**46ポイント**、ハンセン指数を**52ポイント**上回った。

**2025年の超過リターン**：S&P 500を**50ポイント**、ハンセン指数を**39ポイント**上回った。

2年間の累積実運用利益は**146万元超**。主要グローバル指数を2年連続で大きく上回っている。

> *免責：過去の実績は将来の成果を保証しない。スクリーンショットは実際の証券口座（Futu Securities）のものである。*

---

## なぜ普通にAIへ聞くだけでは足りないのか

Claude や ChatGPT に「PDDを買うべきか」と聞けば、たいてい「一方では成長余地があり、他方では競争圧力がある。投資にはリスクがあるので自己判断で」という、整ったが意思決定に使いにくい答えが返ってくる。

**見た目は正しいが、実際の売買判断には弱い。**

AI Berkshire が解くのは「AIが分析できるか」ではない。解くべき問題は、**分析品質と意思決定規律**である。

### 1. 曖昧な両論併記ではなく、結論を強制する

AI Berkshire は **Pass / Fail / Gray Zone**、具体的な価格帯、投資スタイル別の推奨まで出す。結論を避ける分析を許さない。

> 通常のAI回答：*「PDDには成長可能性がある一方、競争圧力も存在するため、投資家は慎重に判断すべきです」*
>
> AI Berkshire の出力例：

> | 戦略 | 推奨 | 価格帯 |
> |------|------|--------|
> | 攻撃型 | 現値で20%ポジション構築 | $95-105 |
> | 中立型 | 自社株買い方針の明確化を待つ | $85-95 |
> | 保守型 | 10年確実性の基準を満たさないため見送り | - |
>
> **ミラーテスト**：5文で説明できないなら買わない。例外なし。

### 2. 単一視点ではなく、4人の投資家の弁証法

単に「バフェット流で分析する」だけではない。4つの視点が互いに衝突し、矛盾をあぶり出す。

PDDの例：

- **段永平**（ビジネスモデル）：良い事業。C2Mモデルは模倣困難 → 3.7/5
- **バフェット**（財務・ valuation）：ネットキャッシュ控除後PERは6.3倍、キャッシュ創出力が高い → 4.4/5
- **マンガー**（反転思考）：見た目ほど堀は深くない。Douyin が3年でGMV 4兆元に到達 → 3.5/5
- **李録**（長期確実性）：経営文化に懸念。10年後の確実性が低い → 2.0/5

**バフェットは「本当に安い」と言い、李録は「確実でないなら買わない」と言う。** この衝突こそ、実際の投資判断の姿である。

### 3. バイアス対策を構造化している

AIの危険は、明らかに間違った答えを出すことだけではない。より危険なのは、**正しそうに見えるが検証に耐えない答え**である。

| 仕組み | 解く問題 | 例 |
|--------|----------|----|
| **情報量評価（A/B/C）** | 「資料が多いほど確実」という錯覚を防ぐ | Pop Mart はB評価。推定値には信頼度を明示 |
| **マンガー式反転検査** | 失敗シナリオを強制的に考える | 「PDDはどう死ぬか」を5シナリオで検討 |
| **Quick-Kill Checklist** | 8つのレッドラインで一票否決 | 経営者の誠実性に問題があれば valuation に関係なく棄却 |
| **反コンセンサス確認** | 市場と同じ見方に流されるのを防ぐ | 「賢い投資家がなぜ空売りしているのか」を確認 |
| **知的誠実性** | わからないことをわからないと残す | データ不足は推測で埋めず Gray Zone と明記 |

### 4. 財務データの精度を重視する

LLMは暗算に弱い。PERを1桁間違える、HKDとCNYを混同する、といったミスは投資判断では致命的である。

Tencent分析時には、時価総額が「香港ドル建て」と「人民元建て」で混在していた。AI Berkshire では次のように手計算を検証する。

```bash
# 時価総額の手動検証：株価 × 発行済株式数を報告値と照合
python3 tools/financial_rigor.py verify-market-cap \
  --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD
# Verified - deviation only 0.08%
```

計算は `float` ではなく Python `decimal.Decimal` による正確な10進演算を使う。重要データは原則として2つ以上の独立ソースで照合する。

### 5. 再現性のあるリサーチプロセス

普通にAIへ聞くと、日によってフォーマット、深さ、論点が揺れる。AI Berkshire は **同じ入力に対して、同じ構造・同じ深さの分析**を返すことを重視する。

- 7社を同じ採点基準で横比較できる
- 6か月後に同じ会社を再分析し、変化を直接比較できる
- 複数人・複数Agentの調査結果を同じ形式で統合できる

### 6. Multi-Agent 並列調査

`/investment-team` は4つの独立Agentを同時に起動し、それぞれが検索・検証・判断を行う。1つのプロンプトを4章に分けるのではなく、4人のアナリストが独立に調査し、Team Lead が最終判断を統合する。

```text
Team Lead
  ├─ Agent 1: ビジネスモデル / 段永平
  ├─ Agent 2: 財務・valuation / バフェット
  ├─ Agent 3: 業界・競争 / マンガー
  └─ Agent 4: リスク・経営陣 / 李録

並列調査 → 相互検証 → 統合レポート
```

### 一言で言うと

> **普通のAI利用では「正しそうな分析」が得られる。AI Berkshire では「実際に意思決定に使える投資リサーチ」を得る。**

---

## アーキテクチャ

<p align="center">
  <img src="assets/architecture.png" alt="AI Berkshire Architecture" width="600" />
</p>

> ソース：[`assets/architecture.mmd`](assets/architecture.mmd)（編集可能な Mermaid 図）

**3層構造**：

- **Skill層**：やりたいことを18個の明確な入口に整理する。深掘り、財報分析、業界スクリーニング、ポートフォリオ管理、思考ツールを用途別に選ぶ。
- **Agent層**：各Skillが複数Agentを並列実行し、独立に検索・判断・相互牽制する。
- **Tool層**：正確な財務計算、Web調査、レポート監査により、データの検証可能性を担保する。

---

## Skill一覧（18 Skills）

### 深掘りリサーチ

| Skill | 用途 | 使う場面 |
|-------|------|----------|
| [`/investment-research`](skills/investment-research.md) | 4人の投資家視点による総合分析 | 上場企業を正面から深掘りする |
| [`/investment-team`](skills/investment-team.md) | Multi-Agent 並列リサーチ | 最速で厚い調査をしたい |
| [`/management-deep-dive`](skills/management-deep-dive.md) | 経営陣の深掘り | 「株を買うことは人に資本を預けること」と考える場面 |
| [`/private-company-research`](skills/private-company-research.md) | 非上場企業調査 | Ant Group、SpaceX のような情報不足企業を調べる |
| [`/deep-company-series`](skills/deep-company-series.md) | 8本構成の長文企業シリーズ | 認知リセットから最終判断まで出版級に整理する |

### 財報分析

| Skill | 用途 | 使う場面 |
|-------|------|----------|
| [`/earnings-review`](skills/earnings-review.md) | 一次資料ベースの財報精読 | セルサイド資料ではなく原資料だけで読む |
| [`/earnings-team`](skills/earnings-team.md) | 財報チーム + 公開用記事 | 4視点で解釈し、編集・読者確認まで行う |

### 業界スクリーニング

| Skill | 用途 | 使う場面 |
|-------|------|----------|
| [`/industry-research`](skills/industry-research.md) | 産業バリューチェーン調査 | 産業全体の投資機会を地図化する |
| [`/industry-funnel`](skills/industry-funnel.md) | 業界ファネル選別 | 全市場から10社以下、最後に3社へ絞る |
| [`/quality-screen`](skills/quality-screen.md) | 7つの硬指標による低品質企業除外 | 個別株・業界・指数・テーマを素早くふるいにかける |
| [`/bottleneck-hunter`](skills/bottleneck-hunter.md) | サプライチェーン瓶頸探索 | 大きなトレンドから物理的制約と裁定機会を探す |
| [`/investment-checklist`](skills/investment-checklist.md) | バフェット式購入前チェックリスト | 10分で「深掘りする価値があるか」を決める |

### ポートフォリオ管理

| Skill | 用途 | 使う場面 |
|-------|------|----------|
| [`/portfolio-review`](skills/portfolio-review.md) | ポートフォリオレビューと最適化 | 銘柄調査から資産配分・集中度・リバランスへ進む |
| [`/thesis-tracker`](skills/thesis-tracker.md) | 投資仮説トラッカー | 購入後に仮説が壊れていないか継続監視する |
| [`/news-pulse`](skills/news-pulse.md) | 株価急変の短時間要因分析 | 急騰・急落時に「何が起きたか」を10分で把握する |

### 思考ツール

| Skill | 用途 | 使う場面 |
|-------|------|----------|
| [`/dyp-ask`](skills/dyp-ask.md) | 段永平式Q&A | 事業・投資・人生の問いを段永平の思考法で考える |
| [`/financial-data`](skills/financial-data.md) | 財務データ取得と交差検証 | 重要データを2つ以上の独立ソースで照合する |
| [`/wechat-article`](skills/wechat-article.md) | WeChat記事ワークフロー | 著者・編集者・読者Agentで公開用記事を作る |

---

## Quick Start

### 1. AIクライアントをインストール

このリポジトリは1つの正本ワークフローを保ち、Claude Code コマンドと Codex Skill の両方を提供する。使うクライアントをインストールする。

Claude Code ユーザー：

```bash
npm install -g @anthropic-ai/claude-code
```

Codex ユーザー：

```bash
# macOS / Linux
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# npm
npm install -g @openai/codex

# Homebrew
brew install --cask codex

# インストール確認
codex --version
```

Windows では公式 PowerShell インストーラを使える。

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

### 2. Skillをインストール

Claude Code ユーザー：

```bash
git clone https://github.com/xbtlin/ai-berkshire.git
cd ai-berkshire
./scripts/install-claude-commands.sh
```

Codex ユーザー：

```bash
git clone https://github.com/xbtlin/ai-berkshire.git
cd ai-berkshire

# Codex skills を ~/.codex/skills に生成・インストール
./scripts/install-codex-skills.sh
```

このリポジトリには2つの入口がある。

- `skills/*.md`：Claude Code コマンドの正本
- `codex-skills/*/SKILL.md`：`skills/*.md` から生成される Codex Skill パッケージ

### 3. 使う

Claude Code では直接呼び出す。

```bash
# 深掘りリサーチ
/investment-research Tencent
/investment-team Meituan
/management-deep-dive Wang Xing, Meituan
/private-company-research SpaceX
/deep-company-series Pinduoduo

# 財報分析
/earnings-review Tencent 2025Q4
/earnings-team PDD 2025 Annual

# 業界スクリーニング
/industry-research Nuclear Power
/industry-funnel AI Compute
/quality-screen Hang Seng Index Constituents
/bottleneck-hunter AI Infrastructure
/investment-checklist Moutai, NVIDIA, Apple

# ポートフォリオ管理
/portfolio-review Tencent 30%, Meituan 20%, Moutai 20%, Cash 30%
/thesis-tracker Pinduoduo
/news-pulse Tencent

# 思考ツール
/dyp-ask Where is Pinduoduo's real moat?
/wechat-article Explain OPD for large language models
```

Codex では Skill 名を自然文で指定する。

```text
investment-research を使って Tencent を調査
earnings-review を使って PDD 2025年決算を分析
industry-funnel を使って AI compute をスクリーニング
bottleneck-hunter を使って AI infrastructure bottleneck を探索
wechat-article を使って OPD の解説記事を書く
```

Codex slash prompt を入れた場合は、Codex を再起動して `/` メニューから選ぶ。通常は次のように表示される。

```text
/prompts:investment-research Tencent
```

---

## 詳細なSkill説明

### 1. `/investment-research` — 4人の投資家による総合分析

単一企業を最も深く分析するフレームワーク。7つのモジュールを順番に実行する。

```text
データ収集 → 事業の本質（段永平） → 堀（バフェット） → 反転思考（マンガー）
  → 経営陣評価（段永平 + バフェット） → 文明的トレンド（李録）
  → Valuation と安全域
```

主な特徴：

- AIリサーチのバイアス認識メカニズム（A/B/C 情報量評価）
- 主要データの複数ソース照合
- 各投資家の追加質問を分析全体に織り込む
- 強気・基準・弱気の3シナリオ valuation と Reverse DCF

### 2. `/investment-team` — Multi-Agent リサーチチーム

4つのAI Agentを並列起動し、実際の投資リサーチチームを模倣する。各Agentは独立に検索・分析・採点し、Team Lead が最終判断を統合する。

### 3. `/investment-checklist` — バフェット式購入前チェックリスト

10分で「深掘りする価値があるか」を判断する6つのゲート。

```text
Gate 1: Circle of Competence（理解できるか）
  ↓
Gate 2: Good Business（経済性は良いか）
  ↓
Gate 3: Moat（競争優位は深いか）
  ↓
Gate 4: Management（経営陣を信頼できるか）
  ↓
Gate 5: Margin of Safety（十分に安いか）
  ↓
Gate 6: Decision Discipline（合理的か、FOMOか）
  ↓
Mirror Test
```

### 4. `/industry-research` — 産業バリューチェーン調査

投資テーマから始め、産業全体の価値連鎖、上場企業、セグメントごとの勝者、ポートフォリオ配分まで整理する。

```text
投資ロジック → バリューチェーン地図 → グローバル上場企業スキャン
  → セグメントリーダーの4視点分析 → ポートフォリオ提案
```

### 5. `/industry-funnel` — 業界ファネル選別

業界・テーマから始め、全市場を段階的に3社へ絞る。

```text
全市場スキャン（30-60社）
  ↓ 5つのバリュー投資フィルター
粗選別 10社以下
  ↓ 詳細分析
詳細候補 10社以下
  ↓ ポートフォリオ補完性で最終選別
3社を4視点で深掘り
  ↓
推奨ポートフォリオ（Core / Satellite / Option） + 行動シグナル
```

`/industry-research` は産業構造と全体像を重視し、`/industry-funnel` は投資候補を絞る選別プロセスを重視する。

### 6. `/private-company-research` — 非上場企業調査

情報が少ない非上場企業向けの「探偵型」リサーチ。IPO資料、親会社資料、資金調達ニュース、業界データから財務データをつなぎ合わせ、信頼度を明示する。

### 7. `/news-pulse` — 株価急変の短時間要因分析

株価が急騰・急落した時に、10-15分で「何が起きたか」を把握するためのフレームワーク。深掘り調査ではなく、狼狽売りや過剰反応を避けるための短時間要因分析である。

分類例：

- Value Event
- Sentiment Fluctuation
- True Cause Unknown
- Mixed

---

## 実例レポート

> 以下はこのフレームワークで生成された実際の投資リサーチレポートである。

| 会社・テーマ | 使用Skill | 中核結論 | レポート |
|--------------|-----------|----------|----------|
| Pinduoduo (PDD) | `/investment-team` | 総合 3.4/5。極めて安いが10年確実性は不足。中程度のポジション向き | [レポートを見る](reports/拼多多/) |
| Tencent (0700.HK) | `/investment-research` | ソーシャル独占 + 優れた資本配分。Forward PER 14倍は合理的から割安 | [レポートを見る](reports/腾讯/) |
| 7社比較 | `/investment-checklist` | Moutai と Tencent は通過。NVIDIA、Meituan、Kuaishou は条件付き。PDD と Pop Mart は Gray Zone | [レポートを見る](reports/多公司对比-checklist-20260408.md) |
| マスター保有銘柄トラッカー | Custom Research | Buffett / Li Lu / Duan Yongping の最新13F保有と PDD 取得単価分析 | [レポートを見る](reports/大师持仓追踪-research-20260408.md) |

---

## 設計思想

### 4人の投資家の方法論統合

```text
              ┌──────────────────┐
              │   Duan Yongping   │
              │  良いビジネスか   │
              │  事業の本質       │
              └────────┬─────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
┌────────┐     ┌──────────┐      ┌────────┐
│ Buffett │     │  Munger   │      │ Li Lu  │
│  Moat   │     │ Inversion │      │ 長期   │
│ Safety  │     │ Risk List │      │ 確実性 │
│ Margin  │     │ Bias Audit│      │ 文明潮流│
└────────┘     └──────────┘      └────────┘
```

4人の投資家は単なる分担ではない。互いに挑戦するために設計されている。

- 段永平が「良いビジネス」と言う → マンガーが「どう死ぬか」を問う
- バフェットが「十分安い」と言う → 李録が「10年後も存在するか」を問う
- 得られるものは4本のレポートの貼り合わせではなく、4つの思考体系の衝突である

### Financial Rigor Tool (`tools/financial_rigor.py`)

| 機能 | コマンド | 解く問題 |
|------|----------|----------|
| **時価総額検証** | `verify-market-cap` | 株価 × 発行済株式数を正確に計算し、単位ミスを検出 |
| **Valuation検証** | `verify-valuation` | PER / PBR / ROE / FCF Yield を正確な10進演算で検証 |
| **複数ソース照合** | `cross-validate` | 同一データを複数ソースで比較し、許容差超過を警告 |
| **3シナリオ valuation** | `three-scenario` | 強気・基準・弱気の目標株価を正確に計算 |
| **Benford検査** | `benford` | 財務データの先頭桁分布から異常を検知 |
| **高精度計算機** | `calc` | 任意の財務式を正確に計算し、LLM暗算を置き換える |

設計原則：財務計算では `float` ではなく `decimal.Decimal` を使う。`0.1 + 0.2 = 0.3` が崩れることを許さない。

---

## Roadmap

- [x] 4人の投資家による総合分析フレームワーク (`/investment-research`)
- [x] Multi-Agent 並列リサーチチーム (`/investment-team`)
- [x] バフェット式購入前チェックリスト (`/investment-checklist`)
- [x] 産業バリューチェーン調査 (`/industry-research` + `/industry-funnel`)
- [x] 非上場企業リサーチ (`/private-company-research`)
- [x] 財務厳密性ツール（正確な10進演算、時価総額検証、複数ソース照合、Benford検査）
- [x] 株価急変の短時間要因分析 (`/news-pulse`)
- [x] 財報精読 (`/earnings-review` + `/earnings-team`)
- [x] ポートフォリオ管理 (`/portfolio-review`)
- [x] 投資仮説トラッカー (`/thesis-tracker`)
- [x] 経営陣深掘り (`/management-deep-dive`)
- [x] 品質スクリーニング (`/quality-screen`)
- [x] 段永平式思考シミュレータ (`/dyp-ask`)
- [x] 企業深掘り長文シリーズ (`/deep-company-series`)
- [ ] AIリサーチレポートと実際の株価推移の過去検証
- [ ] マクロ経済サイクル分析フレームワーク
- [ ] MCP 経由のリアルタイムデータフィード（Wind / Bloomberg / Yahoo Finance）

---

## 免責事項

本プロジェクトは学習・研究目的であり、投資助言ではない。投資にはリスクがあり、最終判断は慎重に行う必要がある。必ず自分でデューデリジェンスを行うこと。

---

## License

MIT License

---

> "The best investment you can make is in yourself." — Warren Buffett
>
> AI Berkshire: すべての人に、自分専用の投資リサーチチームを。

## Star History

このプロジェクトが役に立った場合は、Star を付けてもらえるとありがたい。

[![Star History Chart](https://api.star-history.com/svg?repos=xbtlin/ai-berkshire&type=Date)](https://star-history.com/#xbtlin/ai-berkshire&Date)
