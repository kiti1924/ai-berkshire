# AI Berkshire Global Market Adaptation 仕様書

- 文書ID: `ABG-MARKET-ADAPTATION-SPEC`
- 版: `0.3-draft`
- 状態: Draft
- 対象リポジトリ: `kiti1924/ai-berkshire`
- 推奨配置先: `docs/global-market-adaptation/spec.md`

## 1. 目的

本仕様は、AI Berkshireの「AI上でSkillを呼び出すだけで投資研究を実行できる」という利便性を維持したまま、次の4市場を対象とする共通投資研究システムへ拡張するための要件を定義する。

- 米国市場
- 日本市場
- 上海証券取引所A株市場
- 香港市場

本システムは、常駐サーバー、常時稼働クローラー、外部データベースサーバーを必要としない。利用者がSkillを実行した時だけ必要な資料を取得し、分析し、レポートを生成して終了するオンデマンド方式を標準とする。

## 2. 設計原則

### 2.1 利用者体験の維持

利用者は従来どおり、企業名または証券コードを指定してSkillを呼び出す。

```text
/investment-research 7203
/investment-team AAPL
/investment-research 600519
/investment-team 0700.HK
```

利用者は市場アダプター、API、キャッシュ、データ形式を意識しない。

### 2.2 共通コアと市場別処理の分離

事業品質、モート、財務品質、経営者、競争、長期構造変化、逆向き分析、価値評価は共通コアとして維持する。

次は市場別に切り替える。

- 銘柄識別
- 公式開示の取得先
- 会計項目の正規化
- 株主構造の評価
- 市場固有リスク
- ガバナンス評価
- 評価指標の補正
- データ取得制約

### 2.3 日本人投資家の方法論統合

日本市場では、元の4名の投資家方法論を維持したうえで、次の2名から抽象化した分析原則を追加する。

- 村上世彰型: 資本配分、余剰資本、政策保有株式、非中核資産、親子上場、少数株主保護、価値解放の触媒
- 藤野英人型: 経営者の質、組織能力、企業文化、人的資本、後継者、成長企業・中小型企業の定性評価

人物そのものの口調や人格を模倣してはならない。人物名は方法論の由来説明にのみ使用し、実装上は中立的な責務名へ変換する。

標準4 Agentでは次のように混合する。

| Agent ID | 基礎方法論 | 日本市場で追加する方法論 |
|---|---|---|
| `business_quality` | 段永平型の事業本質分析 | 藤野英人型の経営者・組織・人的資本分析 |
| `financial_capital` | バフェット型の財務・内在価値分析 | 村上世彰型の資本配分・ガバナンス・価値解放分析 |
| `competition_risk` | マンガー型の逆向き分析 | 日本企業特有の組織硬直、承継、少数株主リスク |
| `structural_change` | 李録型の長期構造分析 | 日本の人口動態、産業再編、資本市場改革 |

重要候補を深掘りする場合は、次の2 Agentを独立起動できる。

- `governance_allocator`: 村上世彰型の資本配分・ガバナンス・触媒分析
- `management_organization`: 藤野英人型の経営者・組織・人的資本分析

日本市場以外でも、分析対象企業に該当論点がある場合はこれらの方法論を補助的に適用できる。ただし、日本市場では標準的に適用する。

### 2.4 無料利用範囲

標準機能は無料で利用可能な情報源のみで完結させる。

有料API、有料データベース、商用データフィード、サブスクリプション契約を必須依存にしてはならない。

有料データ源への対応を将来追加する場合も、任意Providerとして分離し、無料標準経路を壊してはならない。

### 2.5 オンデマンド実行

標準実行では次を禁止する。

- 常駐デーモンを必須化すること
- 全市場を定期巡回すること
- 全上場会社の全開示を一括収集すること
- 外部DBサーバーを必須化すること
- 分析指示がない状態でバックグラウンド収集を続けること

監視、通知、定期更新は将来の任意機能として本体から分離する。

### 2.6 ハイブリッドデータ方式

すべての情報を構造化しない。

次だけを構造化する。

- 証券識別情報
- 計算に使用した主要数値
- 出典
- 対象期間
- 取得時刻
- 通貨・単位
- 会計基準
- 検証状態
- 研究実行情報

財報本文、IR資料、経営者発言、業界情報、ニュース、Web記事は原文資料として保持し、Agentが必要な箇所を読む。

## 3. 対象市場

### 3.1 市場プロファイル

| Market ID | 対象 |
|---|---|
| `US` | 米国取引所に上場する売買可能証券 |
| `JP` | 東京証券取引所上場株式 |
| `CN_SH_A` | 上海証券取引所A株 |
| `HK` | 香港証券取引所上場株式 |

市場は発行会社の国籍ではなく、分析対象証券の上場市場で決定する。

米国市場に上場する中国企業ADRは`US`として扱い、同一発行会社の香港株または上海A株とは別証券として識別する。

### 3.2 対象証券

標準対象は普通株式および通常の預託証券とする。

次は初期実装の対象外または専用評価ルートとする。

- ETF
- ETN
- 優先株
- 債券
- オプション
- 先物
- REIT
- 銀行
- 保険
- 証券会社
- SPAC
- 上場前企業

対象外証券を受け取った場合は、誤った通常企業評価を実行せず、`out_of_scope`または専用ルート未実装を返す。

## 4. 標準実行モデル

### 4.1 実行フロー

```text
利用者入力
  ↓
Security Resolver
  ↓
Market Profile選択
  ↓
既存キャッシュ確認
  ↓
必要資料のオンデマンド取得
  ↓
主要Fact抽出・検証
  ↓
企業類型判定
  ↓
共通Agent分析
  ↓
市場固有Overlay
  ↓
総合判断
  ↓
監査
  ↓
レポート・実行記録保存
  ↓
終了
```

### 4.2 実行モード

#### `on_demand`

毎回必要な資料を取得して分析する。キャッシュは利用しなくてもよい。

#### `on_demand_cached`

標準推奨モード。取得済み資料を再利用し、未取得または古い資料だけを取得する。

#### `monitoring`

任意機能。保有・監視銘柄の新規開示を定期確認する。本仕様の必須実装範囲には含めない。

### 4.3 常駐要件

`on_demand`および`on_demand_cached`は常駐プロセスを必要としない。

ローカルキャッシュまたはSQLiteを使用する場合も、Skill実行中だけ開き、終了時に閉じる。

## 5. 論理アーキテクチャ

```text
Skill Layer
├── investment-research
├── investment-team
├── earnings-review
├── quality-screen
└── portfolio-review

Research Core
├── business_quality
├── financial_capital
├── competition_risk
├── structural_change
├── valuation
└── synthesis

Market Layer
├── USMarketAdapter
├── JapanMarketAdapter
├── ShanghaiAMarketAdapter
└── HongKongMarketAdapter

Data Layer
├── Security Resolver
├── Document Retriever
├── Fact Extractor
├── Evidence Registry
├── Financial Validator
└── Optional Local Cache

Output Layer
├── Research Report
├── Fact Snapshot
├── Evidence Index
└── Run Manifest
```

## 6. 導入・配布互換性

### 6.1 基本要件

市場拡張後も、元リポジトリと同じ導入体験を維持しなければならない。

Claude Code利用者は、リポジトリをcloneしてインストールスクリプトを1回実行した後、従来と同じスラッシュコマンドを使用できる。

```bash
git clone git@github.com:kiti1924/ai-berkshire.git
cd ai-berkshire
./scripts/install-claude-commands.sh
```

Codex利用者は、従来と同じSkill生成・インストール手順を使用できる。

```bash
git clone git@github.com:kiti1924/ai-berkshire.git
cd ai-berkshire
./scripts/install-codex-skills.sh

# 任意
./scripts/install-codex-prompts.sh
```

導入後の利用例は次とする。

```text
/investment-research 7203
/investment-team トヨタ自動車
/earnings-review AAPL 最新
/prompts:investment-research 0700.HK
```

市場拡張によって、利用者へMarket Adapter名、内部Agent名、データ取得コマンドの指定を要求してはならない。

### 6.2 正本と生成物

`skills/*.md`をClaude CodeとCodexで共有するcanonical workflowの正本として維持する。

次は生成物または配布物として扱う。

- `codex-skills/*/SKILL.md`
- `codex-prompts/*.md`
- インストール先のClaude Code commands
- インストール先のCodex skills
- インストール先の共有runtime bundle

生成物を直接編集してはならない。変更は正本、生成スクリプト、参照資料へ加え、正式な同期処理で再生成する。

`sync-codex-skills.py --check`相当の検査により、正本とCodex生成物の一致を確認できなければならない。

### 6.3 利用者向けSkillと内部参照資料の分離

利用者向けSkillはトップレベルの`skills/*.md`に置く。

市場別仕様、共通契約、日本人投資家レンズなどの内部参照資料は、利用者向けコマンドとして直接インストールしてはならない。

推奨構成は次とする。

```text
skills/
  investment-research.md
  investment-team.md
  earnings-review.md
  quality-screen.md

  shared/
    agent-contract.md
    evidence-contract.md
    fact-contract.md

  markets/
    us.md
    jp.md
    cn-sh-a.md
    hk.md

  lenses/
    governance-allocator.md
    management-organization.md
```

インストーラーおよび生成処理は、トップレベルSkillだけを利用者向け入口として公開し、必要な内部参照資料を共有runtimeまたは各Codex Skillの`references/`へ同梱する。

### 6.4 Claude Code向け配布

現行のトップレベル`skills/*.md`のコピー動作を維持しつつ、Skillが参照する次の資源も配布する。

- `tools/`
- `config/`
- `schemas/`
- `skills/shared/`
- `skills/markets/`
- `skills/lenses/`

推奨インストール構成は次とする。

```text
~/.claude/
  commands/
    investment-research.md
    investment-team.md
    earnings-review.md
    quality-screen.md

AI_BERKSHIRE_HOME/
  tools/
  config/
  schemas/
  references/
    shared/
    markets/
    lenses/
  install-manifest.json
```

Claude向けコマンドは、clone元の絶対パスではなく`AI_BERKSHIRE_HOME`から共有資源を解決する。

### 6.5 Codex向け配布

Codex Skillは正本である`skills/*.md`から生成する。

各Skillが単独で利用できるよう、必要な参照資料をSkillパッケージへ同梱する。

```text
~/.codex/skills/investment-research/
  SKILL.md
  references/
    shared/
    markets/
    lenses/
  schemas/
```

共有Python toolsを別runtime bundleとして配置する場合は、Skillから`AI_BERKSHIRE_HOME`を経由して解決する。

Codex slash promptsは任意の互換層とし、未導入でもSkill本体は利用可能でなければならない。

### 6.6 clone先非依存

インストール後のSkillは、リポジトリが特定のパスに存在することを前提としてはならない。

次のような固定パス参照を正本または生成物へ残してはならない。

```text
~/ai-berkshire/tools/...
C:\Users\...\ai-berkshire\tools\...
```

インストール後は次のいずれかで資源を解決する。

1. Skillパッケージに同梱した相対パス
2. `AI_BERKSHIRE_HOME`
3. 実行中のworkspace内にある本リポジトリ
4. 明示的な設定値

リポジトリを移動または削除した後も、完全インストール済みSkillが動作する構成を標準とする。

### 6.7 共有runtimeの既定位置

`AI_BERKSHIRE_HOME`が設定されている場合は、その値を優先する。

未設定時の既定位置は次とする。

| 環境 | 既定位置 |
|---|---|
| Linux | `${XDG_DATA_HOME:-$HOME/.local/share}/ai-berkshire` |
| macOS | `$HOME/Library/Application Support/ai-berkshire` |
| Windows | `%LOCALAPPDATA%\ai-berkshire` |

パスに空白や非ASCII文字が含まれても動作しなければならない。

### 6.8 クロスプラットフォーム

次のインストーラー入口を用意する。

- `scripts/install-claude-commands.sh`
- `scripts/install-codex-skills.sh`
- `scripts/install-codex-prompts.sh`
- `scripts/install-claude-commands.ps1`
- `scripts/install-codex-skills.ps1`
- `scripts/install-codex-prompts.ps1`

重複実装を避けるため、ShellおよびPowerShellは共通Pythonインストーラーを呼び出す薄いwrapperとしてよい。

### 6.9 EDINET APIキー

インストール処理は`EDINET_API_KEY`を要求してはならない。

日本株分析でEDINETを使用する時だけ環境変数を参照する。

```text
EDINET_API_KEYあり
  → EDINETを含む通常の日本株分析

EDINET_API_KEYなし
  → TDnet、JPX、会社IR、補助Web情報で分析を継続
  → EDINET未確認を警告
  → 必要に応じてstatusをpartialとする
```

米国、上海A株、香港株の分析では、EDINET APIキーの未設定を警告してはならない。

APIキー入力をSkillの引数、コマンド履歴、レポート本文へ含めてはならない。

### 6.10 更新、再インストール、削除

更新手順は次を標準とする。

```bash
git pull
./scripts/install-claude-commands.sh
./scripts/install-codex-skills.sh
```

インストーラーは冪等でなければならない。

- 同じ版を再実行しても重複を作らない
- 管理対象ファイルだけを更新する
- 他プロジェクトのcommandsまたはskillsを削除しない
- 一時ディレクトリへ生成後、可能な範囲で原子的に置換する
- `install-manifest.json`へ管理対象と版を記録する
- 途中失敗時に利用可能だった旧版を不必要に破壊しない

将来、アンインストーラーを追加する場合はManifestに記録された管理対象だけを削除する。

### 6.11 インストール時の禁止事項

- Dockerの必須化
- Webサーバーの起動
- 常駐プロセスの登録
- cronまたはタスクスケジューラへの自動登録
- APIキーの対話的収集または保存
- 全市場データの事前取得
- ユーザーの既存commands・skillsの全削除
- 管理対象外ファイルの上書き
- clone先の絶対パスの埋め込み

## 7. データ源方針

### 7.1 ソース分類

| Rank | 区分 | 例 |
|---|---|---|
| 100 | 法定・公式開示 | EDINET、SEC、SSE、HKEX |
| 95 | 取引所公式情報 | TDnet、JPX上場会社情報 |
| 90 | 発行会社公式情報 | 各社IR、年報、説明資料 |
| 70 | 構造化二次情報 | 財務情報サービス |
| 60 | 金融ポータル | Yahoo Finance等 |
| 50 | 報道機関 | 通信社、新聞、専門媒体 |
| 40 | アナリスト資料 | 公開レポート、解説 |
| 20 | SNS・掲示板 | 投資家投稿、匿名情報 |

下位ソースは論点発見に利用できるが、重要な財務数値、株式数、配当、自己株式、正式な企業行動の正本にはしない。

### 7.2 Evidence-on-use

Web検索で発見した情報をすべて保存しない。

分析上の主張または計算に実際に使用した情報だけをEvidenceまたはFactへ昇格させる。

```text
Web検索結果
  ↓
Agentが閲覧
  ↓
判断に使用するか
  ├── 使用しない → 永続保存不要
  └── 使用する
       ↓
Evidence登録
       ↓
数値ならFact登録
       ↓
可能な限り公式資料または別ソースで検証
```

## 8. 市場別データ取得仕様

### 8.1 米国市場

#### 正本

- SEC EDGAR
- 会社公式IR
- 会社提出書類

#### 主な対象資料

- 10-K
- 10-Q
- 8-K
- DEF 14A
- Form 4
- Schedule 13D / 13G
- 20-F
- 6-K

#### 補助Web情報

- Yahoo Finance
- StockAnalysis
- Macrotrends
- 報道機関
- 業界資料

SECの公開閲覧APIおよびJSON/XBRLデータを優先する。補助サイトで得た数値は、重要性が高い場合にSECまたは会社資料へ戻って確認する。

### 8.2 日本市場

#### EDINET

- API Version 2を使用する
- APIキーを環境変数から取得する
- APIキーをリポジトリへ保存しない
- 調査対象企業についてオンデマンド取得する
- 同一書類はキャッシュを優先する
- 訂正書類を元書類と関連付ける

環境変数名は次とする。

```text
EDINET_API_KEY
```

#### TDnet

- 無料のWeb閲覧機能を使用する
- 有料TDnet APIを標準依存にしない
- 対象企業を絞ったオンデマンド検索とする
- 同一ドメインへの並列取得を行わない
- 取得済み資料をキャッシュする
- 過剰な短時間アクセスを行わない

#### 東証上場会社情報サービス

次の確認に使用する。

- 基本情報
- 市場区分
- 証券コード
- 開示資料
- ファイリング情報
- コーポレートガバナンス情報

全企業を高頻度巡回せず、銘柄解決または企業調査時に使用する。

#### コーポレートガバナンス報告書

次の評価に使用する。

- 親会社・支配株主
- 資本構成
- 取締役会
- 社外・独立役員
- 内部統制
- 株主対応
- ガバナンス体制

#### 各社IRサイト

次を優先的に取得する。

- 決算説明資料
- 統合報告書
- 中期経営計画
- 株主総会資料
- 事業説明会資料
- KPI・月次資料
- 資本コスト対応資料

IRサイトの構造差を吸収する汎用大量クローラーは作らず、検索・閲覧型Agentで取得する。

#### 補助Web情報

Yahoo Financeその他の金融ポータルを利用できる。

ただし、正式な売上、利益、株式数、配当、自己株式取得、ガバナンス、企業行動は公式資料で確認する。

#### 日本市場固有の投資家レンズ

日本市場では、通常の事業・財務・モート・競争分析に加え、次の2レンズを標準適用する。

##### 村上世彰型レンズ

- 余剰現金と必要運転資金の分離
- 政策保有株式の規模、縮減方針、売却可能性
- 非中核事業・非事業用資産
- 低収益事業への投下資本
- 親子上場と利益相反
- 少数株主保護
- 自社株買いの実行額と消却
- 配当、買戻し、事業再編を含む総合的資本配分
- MBO、TOB、資産売却、持株会社再編等の価値解放触媒
- 資本コスト、ROIC、PBR改善方針の実効性

##### 藤野英人型レンズ

- 経営者の誠実性と過去の約束履行
- 経営者が顧客、従業員、株主をどう捉えているか
- 組織能力と権限移譲
- 企業文化と現場の活力
- 人的資本投資と生産性
- 後継者と経営継続性
- 中小型企業における経営者依存
- 成長企業における再投資余地
- 数値にまだ現れていない組織的成長力
- 短期利益と長期成長投資の整合性

これらは人物の推奨銘柄を再現するものではなく、分析観点を抽象化したものである。

### 8.3 上海A株

#### 正本

- 上海証券取引所の公告
- 会社公式IR
- 法定定期報告
- 臨時公告

#### 補助Web情報

- Yahoo Finance
- 東方財富等の公開金融ポータル
- 報道機関
- 業界資料

次を市場固有の確認対象とする。

- 国有・民営区分
- 実質支配者
- 関連当事者取引
- 株式質権設定
- 政府補助金
- 非経常損益
- 売掛金・棚卸資産
- 制限株式解除
- 大株主の資金占用
- 監査意見
- 企業間保証

### 8.4 香港市場

#### 正本

- HKEXnews
- 会社公式IR
- 年次報告
- 中間報告
- 適時公告
- 持分開示

#### 補助Web情報

- Yahoo Finance
- AASTOCKS
- 報道機関
- 業界資料

次を市場固有の確認対象とする。

- 支配株主
- 少数株主保護
- 関連当事者取引
- 第三者割当
- 希薄化
- 自社株買い
- 持株会社ディスカウント
- CCASS情報
- Stock Connect保有
- A株・H株・ADRとの関係

## 9. 構造化データの最小契約

### 9.1 Security

```yaml
security:
  security_id: string
  issuer_id: string
  market_id: US | JP | CN_SH_A | HK
  ticker: string
  exchange: string
  legal_name: string
  display_name: string
  security_type: string
  trading_currency: string
  reporting_currency: string
  primary_listing: boolean
  identifiers:
    cik: string | null
    edinet_code: string | null
    isin: string | null
    exchange_code: string | null
```

### 9.2 Document

```yaml
document:
  document_id: string
  security_id: string
  document_type: string
  title: string
  published_at: datetime | null
  retrieved_at: datetime
  source_name: string
  source_type: string
  source_url: string
  local_cache_path: string | null
  content_hash: string | null
  language: string
  is_official: boolean
  supersedes_document_id: string | null
```

### 9.3 Fact

```yaml
fact:
  fact_id: string
  security_id: string
  metric: string
  value: number | string | boolean
  unit: string | null
  currency: string | null
  period_start: date | null
  period_end: date | null
  as_of: datetime | null
  retrieved_at: datetime
  source_document_id: string | null
  source_url: string
  source_rank: integer
  accounting_standard: string | null
  consolidation: consolidated | standalone | unknown
  fact_type: reported | forecast | estimate | normalized
  verification_status: unverified | single_source | cross_checked | official
```

### 9.4 Evidence

```yaml
evidence:
  evidence_id: string
  claim_id: string
  statement: string
  source_document_id: string | null
  source_url: string
  source_rank: integer
  published_at: datetime | null
  retrieved_at: datetime
  supports_claim: boolean
  confidence: low | medium | high
```

### 9.5 Research Run

```yaml
research_run:
  run_id: string
  started_at: datetime
  completed_at: datetime | null
  query: string
  resolved_security_id: string
  market_id: string
  mode: on_demand | on_demand_cached
  as_of: datetime
  skill: string
  documents_used: [string]
  facts_used: [string]
  warnings: [string]
  status: completed | partial | failed
```

## 10. キャッシュと永続化

### 10.1 必須要件

永続キャッシュは必須ではない。

キャッシュが存在しない環境でも分析を実行できなければならない。

### 10.2 推奨構成

```text
data/
  cache/
    US/
    JP/
    CN_SH_A/
    HK/
  facts/
  evidence/
  research-runs/

reports/
  US/
  JP/
  CN_SH_A/
  HK/
```

### 10.3 保存対象

永続保存を推奨するものは次である。

- 生成レポート
- 使用した公式文書
- 主要Fact
- Evidence一覧
- 取得時刻
- 検証結果
- 実行Manifest

短期キャッシュでよいものは次である。

- 一般検索結果
- ニュース一覧
- 金融ポータルの一時HTML
- 重複する検索スニペット
- 分析に使用しなかった資料

### 10.4 SQLite

SQLiteは任意とする。

導入する場合もローカル単一ファイルとし、常駐DBサーバーを要求しない。

## 11. Webアクセス制御

### 11.1 共通制御

```yaml
web_access:
  cache_first: true
  max_concurrent_requests_per_domain: 1
  minimum_interval_seconds: 3
  exponential_backoff: true
  respect_retry_after: true
  stop_on_403: true
  stop_on_repeated_429: true
  bulk_crawling: false
```

数値は設定可能とし、各サイトの規約、robots、応答、明示的制限がより厳しい場合はそちらを優先する。

### 11.2 禁止事項

- CAPTCHA回避
- アクセス制御回避
- ログイン制限の迂回
- robotsまたは利用条件に反する収集
- 短時間の大量並列アクセス
- 同一文書の不要な再取得
- 有料情報の無断取得
- APIキーのハードコード
- 利用者が指定していない全市場バックフィル

### 11.3 障害時動作

403、429、503またはアクセス制限を検出した場合は、別URLを乱用して迂回せず、次の順で処理する。

1. キャッシュ確認
2. 待機とバックオフ
3. 会社IRまたは別の公式無料ソース
4. 二次情報で補完
5. 情報不足を明示して部分レポートを生成

## 12. Agent実行契約

### 12.1 標準Agent

| Agent ID | 責務 | 主な方法論 |
|---|---|---|
| `business_quality` | 顧客価値、事業本質、モート、経営者、組織、人的資本 | 段永平型 + 藤野英人型 |
| `financial_capital` | 財務品質、価値評価、資本配分、ガバナンス、価値解放 | バフェット型 + 村上世彰型 |
| `competition_risk` | 競争、失敗経路、反証、リスク | マンガー型 |
| `structural_change` | 長期需要、技術、政策、産業構造 | 李録型 |

市場固有論点はMarket Adapterが共通Agentへ入力する。

日本市場では、`business_quality`に藤野英人型の経営者・組織評価を、`financial_capital`に村上世彰型の資本配分・ガバナンス評価を必ず追加する。

### 12.2 深掘りAgent

重要候補、判断が分かれる企業、資産価値企業、親子上場企業、成長企業、中小型企業では、次のAgentを独立起動できる。

| Agent ID | 責務 | 方法論の由来 |
|---|---|---|
| `governance_allocator` | 余剰現金、政策保有株式、非中核資産、事業再編、親子上場、少数株主保護、触媒 | 村上世彰型 |
| `management_organization` | 経営者の誠実性、意思決定、組織能力、企業文化、人的資本、承継、成長余地 | 藤野英人型 |

深掘りAgentの出力は標準Agentを置き換えるものではなく、標準4 Agentの結論を検証・補強する。

### 12.3 データ取得と分析の分離

各Agentが独立して同じ財務数値をWeb検索してはならない。

主要財務Factは共通の取得・検証ステップで作成し、全Agentが同じFact Snapshotを参照する。

Agentは追加調査を行えるが、新たな重要数値を使用する場合はEvidenceまたはFactへ登録する。

### 12.4 人物名の扱い

バフェット、マンガー、段永平、李録、村上型、藤野型などは方法論の由来説明に使用できる。

実装上のAgent IDは人物名ではなく、分析責務を表す中立名称とする。

## 13. 分析品質要件

### 13.1 数値検証

次は原則として計算元の数値から再計算する。

- 時価総額
- PER
- PBR
- ROE
- FCF
- FCF利回り
- ネットキャッシュ
- EV
- 株主還元利回り

第三者サイトの表示値だけをそのまま採用しない。

### 13.2 重要数値の優先順位

```text
訂正後公式開示
> 最新公式開示
> 取引所公式情報
> 会社IR
> 信頼できる二次情報
> 金融ポータル
> その他Web情報
```

### 13.3 不確実性

取得不能、定義差、単位差、会計基準差、時点差がある場合は、無理に単一値へ統合しない。

次を出力できる。

- レンジ
- 複数値
- 未検証
- 推定
- 不明
- 資料不足

## 14. 出力仕様

### 14.1 レポート

標準保存先は次とする。

```text
reports/{market_id}/{ticker}-{issuer_slug}/{YYYYMMDD}-{skill}.md
```

### 14.2 付随ファイル

```text
reports/{market_id}/{ticker}-{issuer_slug}/{run_id}/
  report.md
  facts.json
  evidence.json
  documents.json
  run-manifest.json
```

付随ファイルを生成しない簡易モードも許容するが、レポート本文には主要出典と分析時点を記載しなければならない。

### 14.3 レポート必須情報

- 対象証券
- 上場市場
- 分析時点
- 価格時点
- 使用通貨
- 会計基準
- 主要出典
- データ不足
- 推定値
- 反証条件
- AI分析の信頼度
- 免責

## 15. 設定と秘密情報

### 15.1 環境変数

```text
EDINET_API_KEY
AI_BERKSHIRE_HOME
AI_BERKSHIRE_CACHE_DIR
AI_BERKSHIRE_REPORT_DIR
AI_BERKSHIRE_WEB_MIN_INTERVAL_SECONDS
AI_BERKSHIRE_CACHE_ENABLED
CLAUDE_COMMANDS_DIR
CODEX_HOME
```

### 15.2 秘密情報

APIキー、Cookie、セッション情報、個人情報を次へ保存してはならない。

- Git管理対象
- レポート
- 実行ログ
- Evidence
- エラーメッセージ

`.env.example`には変数名だけを記載する。

## 16. 非機能要件

### 16.1 再現性

同一の`as_of`、同一Fact Snapshot、同一文書集合を使用した場合、主要数値と出典が一致しなければならない。

### 16.2 可搬性

次の環境で動作できる構成を優先する。

- Claude Code
- Codex
- ローカルCLI
- 一般的なPython環境
- Windows PowerShell
- macOS / Linux Shell

特定の常駐クラウドサービスへ依存しない。

インストール後の動作はclone先の絶対パスへ依存してはならない。パスに空白、日本語、その他の非ASCII文字が含まれても、Skill、参照資料、schemas、toolsを解決できなければならない。

### 16.3 劣化動作

一部ソースへ接続できなくても、利用可能な資料で分析を継続し、欠落を明示する。

### 16.4 監査可能性

重要な主張について、どの文書またはWeb情報を根拠としたか追跡できなければならない。

## 17. 初期実装範囲

### Phase 0: 仕様・契約

- 本仕様
- Security schema
- Document schema
- Fact schema
- Evidence schema
- Research Run schema

### Phase 1: 導入・配布互換性

- Claude Code commandsインストール
- Codex skills生成・インストール
- Codex prompts任意インストール
- 内部参照資料の同梱
- 共有runtime bundle
- `AI_BERKSHIRE_HOME`
- Shell / PowerShell対応
- clone先非依存
- 冪等インストール
- install manifest
- 生成物同期検査
- EDINETキー未設定時の劣化動作

### Phase 2: 市場判定とSecurity Resolver

- `US`
- `JP`
- `CN_SH_A`
- `HK`
- クロスリスティング識別
- 曖昧なTickerの検出

### Phase 3: 無料データ取得

- SEC
- EDINET
- TDnet Web
- JPX上場会社情報
- JPXガバナンス情報
- SSE公告
- HKEXnews
- 会社IR
- 補助Web検索

### Phase 4: Fact Snapshot

- 主要財務数値
- 株式数
- 株価
- 時価総額
- 通貨・単位
- 出典
- 検証状態

### Phase 5: Market Adapter

- 米国固有論点
- 日本固有論点
- 上海A株固有論点
- 香港固有論点

### Phase 6: Skill統合

- investment-research
- investment-team
- earnings-review
- quality-screen

### Phase 7: キャッシュ・監査

- ファイルキャッシュ
- 任意SQLite
- Evidence監査
- 数値再計算
- アクセス制御テスト

## 18. 受入条件

次をすべて満たした時、本仕様の初期実装を完了とする。

1. 4市場の証券を自動判定できる
2. 利用者は従来どおりSkillへ企業名またはTickerを渡すだけでよい
3. Claude Codeで元リポジトリと同じ1回のインストール操作により利用できる
4. Codexで元リポジトリと同じSkill生成・インストール操作により利用できる
5. Codex slash promptsを導入しなくてもCodex Skill本体を利用できる
6. トップレベルSkillだけが利用者向けコマンドとして公開される
7. 市場別・共通・投資家レンズの内部資料が実行時に解決できる
8. インストール後の動作がclone先の絶対パスに依存しない
9. clone元を移動または削除しても完全インストール済みSkillが動作する
10. ShellおよびPowerShellから導入できる
11. インストーラーを複数回実行しても重複や破損が生じない
12. インストーラーが他プロジェクトのcommands・skillsを削除しない
13. canonical `skills/*.md`とCodex生成物の同期を自動検査できる
14. インストール時にDocker、Webサーバー、常駐プロセスを要求しない
15. インストール時にAPIキーを要求または保存しない
16. `EDINET_API_KEY`未設定でも日本株分析を劣化動作で継続できる
17. 米国・上海A株・香港株の分析ではEDINETキー未設定警告を出さない
18. 常駐プロセスなしで分析を完了できる
19. 有料データ源なしで標準分析を完了できる
20. TDnet・JPX等へ大量並列アクセスしない
21. Yahoo Finance等の補助Web情報を使用できる
22. 重要数値は出典・時点・単位を追跡できる
23. 公式資料と二次情報が競合した場合の優先順位が機能する
24. 一部情報が取れない場合も不足を明示して部分完了できる
25. 同じFact Snapshotを全Agentが共有する
26. 市場固有論点がMarket Adapter経由で適用される
27. レポートから主要根拠へ追跡できる
28. 日本市場では村上世彰型と藤野英人型の分析観点が標準4 Agentへ混合される
29. 必要に応じて`governance_allocator`と`management_organization`を独立起動できる
30. APIキーや秘密情報がレポート・Git・ログへ漏れない
31. キャッシュを無効化しても実行できる

## 19. 非対象

本仕様の初期実装には次を含めない。

- 自動売買
- 証券会社APIへの発注
- リアルタイム株価配信
- 全市場常時監視
- 全開示の自動アーカイブ
- 有料データ契約
- ポートフォリオ最適化
- 税務判断
- 法的投資助言
- バックテスト基盤
- モバイルUI
- Webアプリ常駐サーバー

## 20. 下位仕様書

本仕様を上位正本とし、次を下位仕様として別文書化する。

```text
docs/global-market-adaptation/
  spec.md
  data-contract.md
  security-resolution.md
  agent-contract.md
  scoring-contract.md
  report-contract.md
  access-policy.md
  installation-contract.md
  packaging-contract.md
  markets/
    us.md
    jp.md
    cn-sh-a.md
    hk.md
```

下位仕様が本仕様と矛盾する場合は、本仕様を優先する。

## 21. 正本となる決定

1. 対象市場は`US`、`JP`、`CN_SH_A`、`HK`の4市場とする
2. 標準動作はオンデマンド実行とする
3. 常駐処理は必須にしない
4. 無料情報源のみで標準機能を完結させる
5. 全面構造化を行わない
6. 計算・再現・監査に必要なFactだけを構造化する
7. 財報・IR・ニュースは原文検索を維持する
8. 補助金融ポータルを排除しない
9. 重要数値は公式資料へ遡って検証する
10. キャッシュは推奨するが必須にしない
11. 監視機能は研究本体から分離する
12. 投資研究コアは共通化し、市場固有差はMarket Adapterへ集約する
13. 日本語の標準用語は「モート」とする
14. 日本市場では村上世彰型の資本配分・ガバナンス分析を標準導入する
15. 日本市場では藤野英人型の経営者・組織・人的資本分析を標準導入する
16. 通常は既存4 Agentへ混合し、重要案件では2 Agentを独立起動する
17. 元リポジトリと同じインストール操作とSkill呼出し体験を維持する
18. `skills/*.md`をClaude CodeとCodexのcanonical workflowとする
19. 内部参照資料は利用者向けコマンドとして公開せず、runtimeまたはSkillへ同梱する
20. インストール後の動作をclone先の絶対パスへ依存させない
21. Claude CodeとCodexのインストーラーは冪等かつ管理対象限定とする
22. Codex生成物は正本から正式な同期処理で生成する
23. EDINET APIキーはインストール条件とせず、実行時の任意設定とする
24. APIキー未設定時は利用可能な無料ソースで劣化動作し、欠落を明示する
25. 導入時にDocker、常駐サービス、全市場データ取得を要求しない
