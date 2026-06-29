# AI Berkshire Global Market Adaptation — Goalタスク実行指示書

- 文書ID: `ABG-GOAL-INSTRUCTIONS`
- 版: `0.1-draft`
- 対象リポジトリ: `kiti1924/ai-berkshire`
- 上位正本: `docs/global-market-adaptation/spec.md`
- 上位仕様版: `ABG-MARKET-ADAPTATION-SPEC 0.3-draft`
- 推奨配置先: `tasks/global_market_adaptation/README.md`
- CHAIN_ID: `AI-BERKSHIRE-GLOBAL-MARKET-ADAPTATION`
- Integration branch: `integration/global-market-adaptation`
- Required Base SHA: 実行開始時に利用者が指定する実SHA

---

## 1. 目的

本指示書は、AI Berkshireの既存の利用体験を維持しながら、米国、日本、上海A株、香港株へ対応するオンデマンド型投資研究基盤を、Goal単位で安全かつ検証可能に実装するための完全な実行指示である。

実装後も、利用者は従来どおり企業名またはTickerをSkillへ渡すだけでよい。

```text
/investment-research 7203
/investment-team AAPL
/investment-research 600519
/investment-team 0700.HK
```

次を必須要件とする。

- 常駐サービスを必須にしない
- Docker、外部DB、Webサーバーを必須にしない
- 無料情報源だけで標準分析を完結させる
- 全情報を構造化せず、分析に使用する主要FactとEvidenceだけを構造化する
- 元リポジトリと同じClaude Code・Codex導入体験を維持する
- 日本語では「モート」を標準用語とする
- 日本市場へ村上世彰型および藤野英人型の分析観点を導入する
- APIキー、Cookie、秘密情報をGit、ログ、レポートへ漏らさない
- 実サイトへの過剰アクセスを行わない

---

## 2. 正本と優先順位

実装時の仕様優先順位は次とする。

1. `docs/global-market-adaptation/spec.md`
2. 本指示書
3. Goalごとの下位仕様・schema・契約
4. 既存のリポジトリ内規約
5. 既存実装

下位文書または既存実装が上位正本と矛盾する場合は、上位正本を優先する。

上位仕様が曖昧な場合は、次の原則で解決する。

- 利用者体験を変えない
- オンデマンド実行を優先する
- 無料・公式ソースを優先する
- 最小限の構造化に留める
- 既存Skillとの後方互換性を維持する
- 秘密情報を要求しない
- 外部アクセスを減らす
- 不明な情報を推測で埋めない

---

## 3. 作業開始条件

各Goalの開始時に、必ず実際のGit状態から次を確認する。

- 対象リポジトリが`kiti1924/ai-berkshire`であること
- `origin`のURL
- 現在branch
- `HEAD`
- `origin/<base branch>`のSHA
- Required Base SHAとの一致
- working treeの変更
- untracked files
- 既存worktree一覧
- integration branchの有無とHEAD
- 上位仕様書の存在・版・内容
- 前Goalの完了記録と実commit SHA
- canonical SkillとCodex生成物の同期状態
- 既存テストの基準結果

開始条件が成立しない場合は、勝手にreset、stash、削除、上書きを行わない。安全に解決できる既知の差分でない限り、`blocked`として実状態を報告する。

未コミット差分が利用者の作業である可能性がある場合は保持する。別worktreeを作成して隔離する。

---

## 4. Git・worktree運用規則

### 4.1 Integration branch

```text
integration/global-market-adaptation
```

Required Base SHAから作成する。

### 4.2 Goal branch

各Goalは、その開始時点の最新integration HEADから独立branchを作成する。

```text
goal/gma-00-foundation
goal/gma-01-installation
goal/gma-02-contracts
...
goal/gma-13-final-acceptance
```

### 4.3 Worktree

各Goalは独立worktreeで実施する。既存作業コピーを破壊しない。

### 4.4 Commit

原則として各Goalは1つの主commitにまとめる。

- 生成物更新を含める
- focused testを実行する
- `git diff --check`を通す
- integration branchへ`--ff-only`で統合する
- integration branchをremoteへpushする

修復が必要な場合も、Goal commit後に無関係な修正を重ねない。Goal受入条件を満たすための修正はGoal branch内で整理してから統合する。

### 4.5 禁止事項

- `git reset --hard`による利用者差分の破棄
- 無断のforce push
- integration branchへの直接作業
- 複数Goalの混在commit
- Goal外の大規模整形
- 生成物だけの手編集
- テストを無効化して通すこと
- 既存のローカライズ成果を英語・中国語へ戻すこと

---

## 5. 共通実装規則

### 5.1 Canonical naming

新規実装では、同一概念に複数名称を導入しない。

推奨canonical名は次とする。

```text
market_id
security_id
issuer_id
document_id
fact_id
evidence_id
run_id
retrieved_at
published_at
as_of
source_rank
verification_status
accounting_standard
trading_currency
reporting_currency
```

旧名称が存在する場合も、runtime aliasを無制限に増やさない。必要な互換性は境界で一方向に正規化する。

### 5.2 Market ID

利用可能な市場IDは次の4つだけとする。

```text
US
JP
CN_SH_A
HK
```

文字列の別名や曖昧な市場コードを内部canonical値として保存しない。

### 5.3 用語

日本語文書、Prompt、Skill、レポートでは「モート」を使用する。「護城河」を新規追加しない。

### 5.4 ネットワーク

自動テストは原則として実ネットワークへ接続しない。

- HTTPはfixtureまたはmockで再現する
- 実サイトのHTML/PDFは利用条件に配慮した最小fixtureを使用する
- APIキーをCIへ要求しない
- live smoke testは明示的なopt-inにする
- live testを標準受入条件にしない
- 大量取得、全市場巡回、短時間並列アクセスをテストしない

### 5.5 秘密情報

次をログ、例外、snapshot、fixture、レポートへ出力しない。

- `EDINET_API_KEY`
- Cookie
- Authorization header
- セッション情報
- 個人情報
- ローカル絶対パス中の利用者名

### 5.6 依存関係

重い依存関係を安易に追加しない。

新規依存を追加する場合は、次を満たす。

- 標準ライブラリで代替困難
- ライセンスが適合
- Windows、macOS、Linuxで導入可能
- lockfileまたは依存定義を更新
- optional dependencyにできるものはoptional化
- 依存未導入時のエラーを明確にする

### 5.7 生成物

`skills/*.md`をcanonical workflowとし、Codex SkillとPromptは正式な同期スクリプトから生成する。

生成物の差分がある場合は、正本またはgeneratorを修正して再生成する。

---

## 6. Goal一覧

| Goal | 名称 | 主な成果物 | 依存 |
|---:|---|---|---|
| 0 | Foundation and task contracts | 正本配置、下位仕様、queue、検証基盤 | なし |
| 1 | Installation and packaging compatibility | Claude/Codex導入、runtime bundle、Manifest | Goal 0 |
| 2 | Canonical data contracts | Security/Document/Fact/Evidence/Run schema | Goal 0 |
| 3 | Security resolution and market routing | 4市場判定、銘柄解決、対象外判定 | Goal 2 |
| 4 | Access policy, retrieval, and cache | HTTP制御、文書取得、キャッシュ | Goal 1, 2 |
| 5 | Fact snapshot and financial validation | Fact抽出、検証、計算、Evidence-on-use | Goal 2, 4 |
| 6 | US market adapter | SEC/IR経路、米国固有分析 | Goal 3–5 |
| 7 | Japan market adapter | EDINET/TDnet/JPX/IR、日本固有分析 | Goal 3–5 |
| 8 | Shanghai A market adapter | SSE/IR経路、上海A固有分析 | Goal 3–5 |
| 9 | Hong Kong market adapter | HKEXnews/IR経路、香港固有分析 | Goal 3–5 |
| 10 | Agent methodology integration | 標準4 Agent、日本人投資家2レンズ | Goal 5–9 |
| 11 | Skill and Codex workflow integration | 既存Skill統合、生成物同期 | Goal 1, 3–10 |
| 12 | Reports, audit, and degraded operation | report/facts/evidence/manifest、監査 | Goal 5, 10, 11 |
| 13 | End-to-end acceptance and final review | 4市場E2E、導入互換性、最終監査 | Goal 0–12 |

---

# Goal 0: Foundation and task contracts

## 目的

上位仕様をリポジトリ内の正本として配置し、以後のGoalを機械的に検証できる契約、queue、検査入口を整備する。

## 必須作業

1. `docs/global-market-adaptation/spec.md`へ上位仕様を配置する。
2. 次の下位仕様を作成する。

```text
docs/global-market-adaptation/
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

3. 次のタスク管理ファイルを配置する。

```text
tasks/global_market_adaptation/
  README.md
  goal_spec.md
  queue.json
  queue.md
  audit.json
```

4. `queue.json`にはGoal 0–13のID、依存、状態、受入条件を記録する。
5. `audit.json`には仕様要件とGoalの対応表を記録する。
6. 文書内の市場ID、Agent ID、schema名、用語を検査する軽量quality gateを追加する。
7. 「護城河」の新規混入を検出する。
8. Goal未実装状態ではproduct codeを変更しない。

## 受入条件

- 上位仕様と下位仕様の参照関係が明確
- Goal 0–13の依存関係が循環しない
- 仕様要件が少なくとも1つのGoalへ割り当てられている
- `queue.json`と`queue.md`の内容が一致
- canonical IDの重複・表記ゆれを検出できる
- 既存Skill・生成物へ意図しない差分がない
- 文書検査、JSON parse、`git diff --check`が成功

## focused test

- JSON schema/parse test
- task queue consistency test
- terminology gate
- document link/path gate
- existing generator `--check`

---

# Goal 1: Installation and packaging compatibility

## 目的

元リポジトリと同じ導入操作を維持しつつ、市場別資料、schema、toolsを正しく配布する。

## 必須作業

1. Claude Code向けインストーラーを拡張する。
2. Codex Skill生成・インストーラーを拡張する。
3. Codex Promptの任意インストールを維持する。
4. `AI_BERKSHIRE_HOME`を導入する。
5. OS別既定runtime pathを実装する。
6. 内部参照資料を利用者向けcommandとして露出させず同梱する。
7. clone元の絶対パス依存を除去する。
8. `install-manifest.json`を導入する。
9. 冪等再インストールを保証する。
10. ShellとPowerShell入口を用意する。
11. install処理でAPIキーを要求しない。
12. 他プロジェクトのcommands/skillsを削除しない。
13. 一時出力後の置換など、失敗時に旧版を破壊しにくい方式を採用する。

## 必須テスト

- 一時HOMEへのClaude install
- 一時CODEX_HOMEへのCodex install
- 2回連続install
- clone元移動後の参照解決
- 空白・日本語を含むpath
- 既存の無関係Skill保持
- Manifest内容
- generated Skill同期
- PowerShell scriptの構文またはWindows CI
- APIキーなしinstall

## 受入条件

- 元のコマンド名で利用できる
- internal referencesがcommand一覧へ混入しない
- clone先に依存しない
- 再実行で重複しない
- `EDINET_API_KEY`なしでinstall成功
- Docker、常駐登録、データ事前取得を行わない

---

# Goal 2: Canonical data contracts

## 目的

Security、Document、Fact、Evidence、Research Runのcanonical contractを実装する。

## 必須作業

1. schemaを作成する。
2. Python側の型またはvalidation modelを作成する。
3. serialize/deserializeを実装する。
4. timezone-aware datetimeを要求する。
5. 通貨・単位・期間・会計基準・連結区分を明示する。
6. `verification_status`をcanonical enum化する。
7. 不明値をゼロや空文字へ変換しない。
8. 任意SQLiteを導入する場合も、schemaとファイル表現を一致させる。
9. 旧表記が存在する場合は入力境界で一方向正規化する。

## canonical contract

### Security

- `security_id`
- `issuer_id`
- `market_id`
- `ticker`
- `exchange`
- `legal_name`
- `display_name`
- `security_type`
- `trading_currency`
- `reporting_currency`
- `primary_listing`
- identifiers

### Document

- `document_id`
- `security_id`
- `document_type`
- `title`
- `published_at`
- `retrieved_at`
- `source_name`
- `source_type`
- `source_url`
- `local_cache_path`
- `content_hash`
- `language`
- `is_official`
- `supersedes_document_id`

### Fact

- `fact_id`
- `security_id`
- `metric`
- `value`
- `unit`
- `currency`
- `period_start`
- `period_end`
- `as_of`
- `retrieved_at`
- `source_document_id`
- `source_url`
- `source_rank`
- `accounting_standard`
- `consolidation`
- `fact_type`
- `verification_status`

### Evidence

- `evidence_id`
- `claim_id`
- `statement`
- `source_document_id`
- `source_url`
- `source_rank`
- `published_at`
- `retrieved_at`
- `supports_claim`
- `confidence`

### Research Run

- `run_id`
- `started_at`
- `completed_at`
- `query`
- `resolved_security_id`
- `market_id`
- `mode`
- `as_of`
- `skill`
- `documents_used`
- `facts_used`
- `warnings`
- `status`

## 必須テスト

- schema validation
- JSON round trip
- invalid enum rejection
- naive datetime rejection
- null handling
- currency/unit distinction
- canonical field precedence
- unknown field policy
- deterministic serialization

---

# Goal 3: Security resolution and market routing

## 目的

企業名、Ticker、証券コードから対象証券と市場を解決し、4市場のMarket Adapterへ振り分ける。

## 必須作業

1. `SecurityResolver`を実装する。
2. `MarketRouter`を実装する。
3. 次を解決する。

```text
AAPL      → US
7203      → JP
7203.T    → JP
600519    → CN_SH_A
600519.SS → CN_SH_A
0700.HK   → HK
700       → 曖昧性を解消してHK候補
```

4. 企業名検索に対応する。
5. ADRと原株を同一Securityとして統合しない。
6. issuerとsecurityを分離する。
7. ambiguous queryは候補を返し、誤決定しない。
8. ETF、REIT、銀行、保険等の初期対象外を判定する。
9. 利用者にMarket Adapter名の指定を要求しない。
10. resolver結果に根拠とconfidenceを含める。

## 必須テスト

- 4市場の代表Ticker
- suffix付き・なし
- leading zero
- ASCII/全角入力
- 日本語・英語・中国語企業名
- ADRと香港株
- 同名企業
- 不明Ticker
- 対象外security type
- deterministic candidate ordering

---

# Goal 4: Access policy, retrieval, and cache

## 目的

オンデマンド文書取得、Webアクセス制御、キャッシュ、リトライ、失敗時の安全な劣化を共通基盤として実装する。

## 必須作業

1. domain別rate limitを実装する。
2. 同一domainの並列数を既定1とする。
3. configurable minimum intervalを実装する。
4. `Retry-After`を尊重する。
5. 403、429、503の扱いを実装する。
6. exponential backoffを実装する。
7. cache-firstを実装する。
8. content hashと取得時刻を保存する。
9. 公式文書の訂正・差し替えを関連付けられるようにする。
10. HTML、JSON、XBRL、PDFのDocument表現を統一する。
11. robots・利用条件・アクセス制限を無視する設計にしない。
12. CAPTCHA回避、ログイン迂回を実装しない。
13. cacheなしでも動作する。
14. SQLiteを採用する場合は任意機能とする。

## 必須テスト

- cache hit/miss
- ETag/Last-Modified相当の扱い
- 429 + Retry-After
- repeated 429停止
- 403停止
- 503 backoff
- concurrent same-domain serialization
- different-domain independence
- corrupted cache
- duplicate document
- cache disabled
- secret redaction

---

# Goal 5: Fact snapshot and financial validation

## 目的

全Agentが共有するFact Snapshot、Evidence-on-use、主要財務計算と検証を実装する。

## 必須作業

1. `FactSnapshot`を実装する。
2. 主要Factのsource、時点、単位、通貨を保持する。
3. source rankに基づく競合解決を実装する。
4. 訂正後公式開示を最優先する。
5. 同期間・同metricでも定義が異なる値を無理に統合しない。
6. Evidence-on-useを実装する。
7. 次を再計算できるようにする。

- market cap
- enterprise value
- net cash
- PER
- PBR
- ROE
- free cash flow
- FCF yield
- shareholder yield

8. `Decimal`等の正確な計算を使用する。
9. 推定値と報告値を区別する。
10. 全Agentが同一snapshotを参照できるAPIを作る。
11. unavailable/unknownを明示する。
12. provenanceをレポートまで追跡可能にする。

## 必須テスト

- source conflict
- official correction
- unit mismatch
- currency mismatch
- consolidated vs standalone
- reported vs estimate
- market-cap recomputation
- divide-by-zero
- negative earnings
- missing shares
- deterministic fact selection
- Evidence登録の有無

---

# Goal 6: US market adapter

## 目的

米国市場向けの無料・公式中心取得と市場固有分析を実装する。

## 必須作業

1. `USMarketAdapter`を実装する。
2. SEC EDGARのCompany Submissions、XBRL等の無料経路へ対応する。
3. 10-K、10-Q、8-K、DEF 14A、Form 4、13D/G、20-F、6-Kを識別する。
4. 会社IRを補完経路にする。
5. Yahoo Finance等をsecondary sourceとして利用可能にする。
6. 次の市場固有チェックを実装する。

- stock-based compensation
- dilution
- buyback net of dilution
- GAAP/non-GAAP差
- goodwill/M&A
- dual-class voting
- founder control
- executive compensation
- antitrust/litigation
- guidance dependence

7. SEC unavailable時にIR・secondary sourceへ劣化し、欠落を警告する。
8. APIキーを要求しない。

## 必須テスト

- domestic issuer
- foreign private issuer
- 10-K/10-Q selection
- amended filing precedence
- multiple share classes
- ADR
- SEC unavailable
- XBRL missing
- secondary-source conflict
- no live network by default

---

# Goal 7: Japan market adapter

## 目的

EDINET、TDnet、JPX、コーポレートガバナンス報告書、会社IRを利用する日本市場Adapterを実装する。

## 必須作業

1. `JapanMarketAdapter`を実装する。
2. `EDINET_API_KEY`を実行時だけ読む。
3. EDINET書類一覧・文書取得をオンデマンドで行う。
4. 訂正書類を優先する。
5. TDnetは対象企業を絞ったWeb閲覧経路とする。
6. JPX上場会社情報とガバナンス情報を利用する。
7. 会社IRから説明資料、統合報告書、中計、株主総会資料等を取得できるようにする。
8. Yahoo Finance等をsecondary sourceとして利用可能にする。
9. 次の日本固有Fact・チェックを実装する。

- excess cash
- treasury shares
- strategic shareholdings
- parent-subsidiary listing
- controlling shareholder
- independent directors
- low-ROIC segments
- non-core assets
- share repurchase authorization/execution/cancellation
- shareholder return
- cost-of-capital/PBR plan
- succession
- FX exposure
- pension obligations
- restructuring/MBO/TOB signals

10. APIキー未設定時もTDnet、JPX、IR、補助Webで継続する。
11. EDINET未確認を明示し、必要なら`partial`とする。
12. 他市場ではEDINETキー警告を出さない。
13. 過剰短時間アクセスを行わない。

## 必須テスト

- EDINET keyあり/なし
- 有価証券報告書
- 訂正報告書
- 大量保有報告書
- TDnet資料
- JPX company profile
- governance report
- IR fallback
- leading-zero handling
- J-GAAP/IFRS/US-GAAP
- consolidated priority
- partial status
- secret redaction

---

# Goal 8: Shanghai A market adapter

## 目的

日本の利用者がアクセス可能な上海A株を対象に、SSE公告と会社IRを中心とするAdapterを実装する。

## 必須作業

1. `ShanghaiAMarketAdapter`を実装する。
2. 上海証券取引所A株だけを標準対象とする。
3. 深圳A株を誤って`CN_SH_A`へ含めない。
4. SSE公告、定期報告、臨時公告、会社IRを正本とする。
5. Yahoo Finance、東方財富等をsecondary sourceとして扱えるようにする。
6. 次の固有チェックを実装する。

- state-owned/private
- ultimate controller
- related-party transactions
- share pledges
- government subsidies
- non-recurring gains
- receivables/inventory
- restricted-share unlocks
- fund occupation
- guarantees
- audit opinion
- policy dependence

7. core earningsとcash conversionを算出可能にする。
8. 中国語文書を原文のままEvidence化できるようにする。
9. 不明な翻訳や単位を推測で確定しない。

## 必須テスト

- 6桁Ticker
- `.SS` suffix
- Shanghai/Shanghai STAR識別
- Shenzhen誤判定防止
- SOE/private flags
- subsidy normalization
- non-recurring item
- RMB unit normalization
- Chinese document metadata
- SSE unavailable fallback

---

# Goal 9: Hong Kong market adapter

## 目的

HKEXnews、会社IR、持分開示等を中心とする香港市場Adapterを実装する。

## 必須作業

1. `HongKongMarketAdapter`を実装する。
2. leading zeroを保持する。
3. HKEXnewsの年報、中間報告、公告、profit warning等を識別する。
4. 持分開示、自己株式取得等を取得対象にする。
5. 会社IRを補完経路にする。
6. Yahoo Finance、AASTOCKS等をsecondary sourceとして扱えるようにする。
7. 次の固有チェックを実装する。

- controlling shareholder
- minority shareholder protection
- connected transactions
- placements/dilution
- buybacks
- holding-company discount
- property revaluation
- mainland exposure
- H-share/red-chip/P-chip
- CCASS/Stock Connect where available
- A/H/ADR relation

8. SOTP、NAV、net cash、dividend+buyback yieldを選択可能にする。
9. HKD/CNY/USDの混同を防ぐ。

## 必須テスト

- `0700.HK`
- numeric input with leading zero
- H-share
- red-chip/P-chip metadata
- annual/interim report
- profit warning
- connected transaction
- placement
- HKD/CNY unit conflict
- HKEX unavailable fallback

---

# Goal 10: Agent methodology integration

## 目的

既存4 Agentへ市場Adapterの情報を供給し、日本市場で村上世彰型・藤野英人型レンズを正式に混合する。

## 必須作業

1. 標準Agent IDを次に統一する。

```text
business_quality
financial_capital
competition_risk
structural_change
```

2. 日本市場では次を必ず混合する。

- `business_quality`へ藤野英人型の経営者・組織・人的資本分析
- `financial_capital`へ村上世彰型の資本配分・ガバナンス・価値解放分析

3. 次の深掘りAgentを追加する。

```text
governance_allocator
management_organization
```

4. 人物の口調、人格、推奨銘柄を模倣しない。
5. 人物名は方法論の由来説明に限定する。
6. 実装上は中立的なAgent IDを使用する。
7. 市場Adapterが固有論点を入力し、Agentが独自に重複取得しないようにする。
8. 全Agentが同一Fact Snapshotを参照する。
9. Agent出力contractを統一する。

推奨出力項目:

- conclusion
- score
- confidence
- claims
- evidence_ids
- fact_ids
- risks
- falsifiers
- unknowns
- warnings

10. 深掘りAgentの起動条件を実装する。

例:

- 親子上場
- 過剰現金
- 政策保有株式
- アクティビスト対象
- MBO/TOB可能性
- オーナー経営中小型
- 後継者問題
- 経営者依存

## 必須テスト

- JPで2レンズ混合
- US/CN/HKで不要な強制適用をしない
- optional deep-dive trigger
- same Fact Snapshot
- conflicting Agent conclusions
- missing evidence
- personality imitation absence
- 「モート」用語gate
- deterministic output contract

---

# Goal 11: Skill and Codex workflow integration

## 目的

市場拡張を既存Skillへ統合し、利用者が新しい内部構造を意識せず利用できるようにする。

## 対象Skill

少なくとも次を統合する。

```text
investment-research
investment-team
earnings-review
earnings-team
quality-screen
investment-checklist
management-deep-dive
portfolio-review
thesis-tracker
news-pulse
```

## 必須作業

1. 入力からSecurity Resolverを呼ぶ。
2. Market Routerを経由する。
3. Fact Snapshotを1回生成して共有する。
4. Market Adapterの固有論点をAgentへ渡す。
5. 既存のSkill名と主要な出力構造を維持する。
6. 市場指定を利用者へ必須にしない。
7. 内部資料参照をClaude/Codex双方で解決する。
8. canonical Skillを修正し、Codex Skill/Promptを再生成する。
9. generator `--check`を通す。
10. 日本語UI/Promptで「モート」を使用する。
11. 既存の中国・米国分析能力を退行させない。
12. SkillがAPIキーを引数へ要求しない。
13. 実行モード`on_demand`/`on_demand_cached`を内部選択できるようにする。

## 必須テスト

- 4市場×主要SkillのPrompt contract
- Claude command install後の参照
- Codex Skill package参照
- generated files freshness
- existing Skill names
- unknown/ambiguous query
- out-of-scope security
- EDINET key missing
- no market adapter argument required

---

# Goal 12: Reports, audit, and degraded operation

## 目的

レポート、Fact、Evidence、Document、Run Manifestを保存し、根拠追跡と劣化動作を保証する。

## 必須作業

1. 標準出力pathを実装する。

```text
reports/{market_id}/{ticker}-{issuer_slug}/{YYYYMMDD}-{skill}.md
```

2. 詳細出力を実装する。

```text
reports/{market_id}/{ticker}-{issuer_slug}/{run_id}/
  report.md
  facts.json
  evidence.json
  documents.json
  run-manifest.json
```

3. 簡易モードも許容する。
4. レポートに次を含める。

- 対象証券
- 市場
- 分析時点
- 価格時点
- 通貨
- 会計基準
- 主要出典
- データ不足
- 推定値
- 反証条件
- confidence
- 免責

5. report auditを4市場対応にする。
6. 数値からsourceまで追跡可能にする。
7. `completed`、`partial`、`failed`を区別する。
8. 一部source失敗時も可能な範囲でレポートを生成する。
9. APIキーやAuthorization情報を出力しない。
10. ローカル絶対パスを利用者向けレポートへ漏らさない。
11. 同一runのfacts/evidence/document参照整合性を検証する。

## 必須テスト

- 4市場fixture report
- partial report
- no-price report
- missing official filing
- evidence link integrity
- fact ID integrity
- secret scan
- path portability
- repeat run comparison
- report audit

---

# Goal 13: End-to-end acceptance and final review

## 目的

Goal 0–12を統合した状態で、上位仕様の全受入条件を検証し、未達・退行・不要な複雑化を除去する。

## 必須作業

1. 上位仕様の受入条件31項目を実際の検査へ対応付ける。
2. 4市場のfixture E2Eを実行する。

推奨代表例:

```text
US      AAPL
JP      7203
CN_SH_A 600519
HK      0700.HK
```

3. Claude install E2Eを実行する。
4. Codex install E2Eを実行する。
5. clone元移動後の動作を検証する。
6. cache有効・無効を検証する。
7. EDINET key有効fixture・未設定を検証する。
8. partial degradationを検証する。
9. 既存Skill regression testを実行する。
10. generated files同期を検証する。
11. secrets scanを実行する。
12. terminology scanを実行する。
13. raw fixed path scanを実行する。
14. network callがmockされていることを確認する。
15. 未使用alias、重複field、dead codeを検査する。
16. docsと実装の一致を確認する。
17. `queue.json`と`audit.json`をcompletedへ更新する。
18. 最終completion reportを作成する。

## 必須品質ゲート

- unit tests
- contract tests
- integration tests
- install tests
- E2E fixture tests
- generator check
- JSON/schema validation
- Python syntax/compile
- shell syntax
- PowerShell syntaxまたはWindows CI
- `git diff --check`
- secret scan
- terminology scan
- fixed-path scan
- no unexpected network access

## 最終受入条件

上位仕様の受入条件31項目すべてに、次のいずれかが記録されていること。

```text
passed
not_applicable（理由必須）
blocked（未完了扱い）
```

`blocked`が1件でもある場合、Goal 13およびCHAIN全体を`completed`としてはならない。

---

## 7. Goal実行手順

各Goalでは次の順序を厳守する。

1. 上位仕様を読む
2. 本指示書を読む
3. Goal対象の下位仕様を読む
4. 現在のGit状態を確認する
5. 前Goalの実commitとintegration HEADを確認する
6. 最新integration HEADからGoal branch/worktreeを作る
7. 既存実装とテストを調査する
8. Goal範囲だけを実装する
9. focused testを実行する
10. full regressionの必要範囲を実行する
11. 生成物を正式手順で再生成する
12. quality gateを実行する
13. Goal branchへcommitする
14. integration branchへff-only統合する
15. integration branchをpushする
16. queue/audit/completion記録を更新する
17. 次Goalの開始条件を報告する

---

## 8. 外部アクセスに関する実行規則

### 8.1 通常のGoal実装・テスト

実サイトへ接続せず、fixture/mockを使用する。

### 8.2 任意のlive smoke

live smokeは次の場合だけ実行できる。

- 利用者が明示的に許可
- 対象sourceの規約に適合
- 少数リクエスト
- APIキーが環境変数で提供済み
- 秘密情報をログへ出さない
- 実取引、注文、証券口座接続を行わない

### 8.3 禁止

- 全銘柄巡回
- 全開示のbackfill
- 高並列取得
- CAPTCHA回避
- 有料情報への無断アクセス
- Cookie流用
- 実証券口座への接続
- 投資注文
- APIキーの作成・表示・保存

---

## 9. Completion report形式

各Goal完了時は、次の形式で報告する。

```text
CHAIN_ID=AI-BERKSHIRE-GLOBAL-MARKET-ADAPTATION
GOAL_ID=<0-13>
STATUS=completed | blocked | partial
REQUIRED_BASE_SHA=<sha>
GOAL_BASE_SHA=<sha>
GOAL_BRANCH=<branch>
GOAL_COMMIT_SHA=<sha>
INTEGRATION_BRANCH=integration/global-market-adaptation
INTEGRATION_HEAD=<sha>
PUSH_STATUS=<status>
WORKTREE=<path>
```

続けて次を記載する。

### 実装内容

- 変更した主要機能
- canonical contract
- 生成物
- migrationまたは互換処理

### 検証結果

```text
focused tests:
full/regression tests:
generator check:
schema validation:
syntax/compile:
git diff --check:
secret scan:
network access:
```

### 受入条件

Goal固有の受入条件を1件ずつ`passed`または`failed`で記録する。

### 未解決事項

- 未解決がなければ`なし`
- `blocked`を隠さない
- 次Goalへ持ち越す場合はqueueへ明記する

### 次Goal開始条件

- 必要なbase SHA
- 前Goal commit
- integration HEAD
- 必要なfixture/schema
- 残存リスク

---

## 10. CHAIN完了条件

次をすべて満たした場合のみCHAIN全体を完了とする。

- Goal 0–13がすべてcompleted
- integration branchが全Goal commitをff-onlyで含む
- integration branchがremoteへpush済み
- 上位仕様の受入条件31項目がすべてpassedまたは妥当なnot_applicable
- `blocked`がない
- canonical SkillとCodex生成物が一致
- 4市場のE2E fixture testが成功
- Claude/Codex install testが成功
- secretsが含まれない
- 実サイトへの過剰アクセスがない
- 常駐サービスを必須にしていない
- 「モート」用語が統一されている
- 日本市場へ村上世彰型・藤野英人型レンズが適用される
- 既存Skillの主要利用方法が維持される
- 最終completion reportが実SHAを含む

---

## 11. 実装しないもの

本CHAINでは次を実装しない。

- 自動売買
- 証券会社API発注
- リアルタイム価格配信
- 常時監視サービス
- 全市場Crawler
- 全開示Archive
- 有料データ契約
- Webアプリサーバー
- 外部DBサーバー必須化
- ポートフォリオ最適化
- バックテスト基盤
- 税務判断
- 法的な投資助言
- 対象外市場の拡張
- 深圳A株対応
- 台湾・韓国・欧州市場対応

これらをGoal達成に必要として追加してはならない。
