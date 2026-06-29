---
name: private-company-research
description: "AI Berkshire Skill: 非上場企業調査：6 Agentによる情報拼図と企業価値評価（原本: skills/private-company-research.md）"
---

## Codexアダプター注記

このSkillは`skills/private-company-research.md`から生成され、Claude CodeとCodexで同じ正本のワークフローを共有する。

- `$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う。
- Windows環境のPowerShellでファイル（SKILL.mdや参照資料）を読み取るコマンドを実行する際は、文字化け（CP932/Unicode誤認識）を防ぐため、必ず `Get-Content -Encoding utf8 -Raw <ファイルパス>` または `python -c "import pathlib; print(pathlib.Path(r'<ファイルパス>').read_text(encoding='utf-8'))"` を使用すること。
- 正本がTask、Agent、WebSearch、Bash、Read、WriteなどClaude Code固有の機能を参照する場合は、このセッションで利用できる最も近いCodex機能へ置き換える。必要に応じてサブエージェント、Web検索、ローカルツール実行用のシェルコマンド、ワークスペース内の通常のファイル編集を使う。
- 共通ツールは本リポジトリの`tools/`から使用する。`~/ai-berkshire/tools/...`を参照するコマンドは、リポジトリを`~/ai-berkshire`へチェックアウトした前提である。必要なら現在のワークスペースのパスを優先する。
- `AGENTS.md`の調査品質規則を維持する。財務データを照合し、評価と計算には精密計算ツールを使い、不確実性と情報源の不足を明示する。

# 非上場企業調査：6 Agentによる情報拼図と企業価値評価

$ARGUMENTS に対して、非上場企業向けの複数Agent調査を行う。Ant Group、Xiaohongshu、SpaceX、Stripeなど、標準化された公開財務諸表が限られる企業を対象とする。

**最終目的**：情報が構造的に不足する状況で、確認可能な証拠と透明な推定を組み合わせ、企業の事業価値rangeを評価する。直近資金調達のheadline valuationを、そのまま内在価値とみなさない。

## 非上場企業特有の問題

- **標準化された財務開示がない**：規制文書、親会社開示、債券資料、media、industry dataなどを組み合わせる必要がある。
- **valuation anchorが少ない**：資金調達、公開peer、DCF、transaction comparisonを併用する。
- **情報非対称性が大きい**：会社側の広報、投資家、従業員、顧客の情報にはそれぞれbiasがある。
- **exitが不確実**：IPO、M&A、secondary transfer、長期非上場など複数scenarioがある。
- **証券ごとの権利が異なる**：preferred stock、liquidation preference、anti-dilutionなどによりheadline valuationと普通株価値が異なる。

## AI調査bias

非上場企業では、AIが次の誤りを起こしやすい。

1. **偽の保守性**：資料が少ないことを、事業の質が低いことと混同する。
2. **偽の精密さ**：空欄を埋めるため、根拠の弱い推定を確定値のように示す。
3. **peer比較への過度な依存**：公開企業のbusiness mixと流動性を無視し、multipleを機械的に適用する。
4. **survivorship・publicity bias**：検索可能な情報が会社側のpositive narrativeに偏る。
5. **古い資金調達価格へのanchoring**：市場、業績、契約条件が変化しても過去valuationを使い続ける。

### 対応原則

- 分からない情報は「確認できない」とする。推測だけで表を完成させない。
- 各重要dataへ情報源、年月、通貨、単位、信頼度を付ける。
- **確認済み事実**、**会社側の説明**、**第三者推計**、**分析上の推定**を明示的に分ける。
- 情報が極端に少ない場合は、完全なtemplateより第一原理の問いを優先する。
  1. 誰のどの問題を解決し、顧客はなぜ支払うのか。
  2. なぜこのteamが勝ち得るのか。
  3. 成功時の上限と、最も現実的な失敗経路は何か。
  4. 次に何を確認すれば仮説を強化・反証できるか。
- 情報非対称性を「alpha」と断定しない。価格発見が非効率である可能性と、単に情報が欠けているriskを両方示す。

### 信頼度

- 🟢 **高**：法定開示、規制文書、監査済み資料、契約当事者の公式開示。
- 🟡 **中**：複数の信頼できる報道、調査会社、公開された投資家資料。
- 🔴 **低**：単一報道、匿名情報、model推定、industry totalからの逆算。
- ⚪ **不明**：根拠を確認できない。

---

## 実行手順

### 手順1：team構成を示す

| 役割 | 責任 | 中核問い |
|---|---|---|
| **team-lead** | 調整、data conflict、cross-check、統合 | 証拠からどこまで判断できるか |
| **business-decoder** | business model、product、顧客 | 顧客価値と収益modelの本質は何か |
| **financial-detective** | 財務拼図、資金調達、valuation | 財務状態と企業価値をどこまで復元できるか |
| **competitive-mapper** | industry structure、競合、代替 | 競争上の位置と破壊経路は何か |
| **risk-governance-analyst** | 経営陣、governance、risk、exit | 誰が統治し、何が永久損失を生むか |
| **tech-ip-analyst** | technology、patent、R&D | 技術優位は実在し、どの程度持続するか |
| **signal-miner** | 公開されたalternative data | 通常開示以外のsignalはnarrativeと整合するか |

### 手順2：teamを作る

TeamCreateを使う。

- `team_name`: `{会社名}-private-research`。英小文字とhyphenを使う。
- `agent_type`: `team-lead`

### 手順3：6つのTaskを作る

TaskCreateで各Taskへ`subject`、`description`、`activeForm`を設定する。

---

## Task 1：business model、product、顧客

- `subject`: `{会社名}のbusiness model、product portfolio、顧客ecosystemを分析する`
- `activeForm`: `{会社名}の事業と顧客を分析中`

### 1. 事業の本質

- 何を、誰へ、どのように提供し、なぜ支払われるかを一文で定義する。
- 会社がなくなった場合の代替手段と、顧客の追加costを確認する。
- 景気後退時にも残る需要か、裁量的支出か。
- 会社側が定義する市場と、顧客が実際に購入する市場を分ける。

### 2. 売上model

- 広告、commission、subscription、transaction fee、financial service、SaaS、hardware、licenseなどの構成。
- business line別の売上比率とtrend。未開示ならrangeまたは不明とする。
- ARPU、take rate、ad load、conversionなどの収益化効率。
- recurringとone-time、契約型とtransaction型、顧客・channel集中。
- revenue recognitionに前倒しの可能性がないか。
- 公開peerとの比較ではbusiness mixと会計定義をそろえる。

### 3. unit economics

- CAC：paid acquisitionとorganic、channel別、規模拡大時の方向。
- LTV：ARPU、gross margin、retention、cross-sellを使い、仮定を示す。
- LTV / CACとpayback period。
- incremental user・transactionのmarginal cost。
- break-even pointとscale economy。

### 4. product portfolioとflywheel

- core、extension、incubation product。
- network effect、data feedback、scale advantageが実際に循環しているか。
- product間のcross-trafficとcannibalization。
- lifecycleと直近12か月の重要update。

### 5. Business Model Canvas

| 要素 | 内容 |
|---|---|
| value proposition | |
| customer segment | |
| channel | |
| customer relationship | |
| revenue stream | |
| key resource | |
| key activity | |
| key partner | |
| cost structure | |

### 6. 顧客

- MAU、DAU、subscriber、active merchantなど、事業に適した指標。
- S-curve上の位置。
- DAU / MAU、利用時間、frequency、retention、churn。
- growthとretentionを分け、paid acquisitionだけの見かけの成長を確認する。
- 年齢、地域、購買力、職業などのuser profile。
- App Store、Google Play、公開されたsocial mediaの評価。platform biasを明記する。
- QuestMobile、Sensor Tower、SimilarWebなどの推計は定義差を確認し、2情報源以上を比較する。

### 7. pricing power

- 過去の値上げ・take rate変更と顧客離脱。
- 競合との価格比較。
- price elasticity。
- value chain内の利益配分に対して、feeが持続可能か。

### 8. 経済的な堀

| 種類 | ★1～5 | 証拠 | trend | 持続性 |
|---|:---:|---|---|---|
| network effect | | | 拡大 / 安定 / 縮小 | |
| switching cost | | | | |
| brand | | | | |
| proprietary data | | | | |
| license・regulation | | | | |
| scale economy | | | | |

総合：広い / 中程度 / 狭い / 確認できない。

### 9. 国際化

海外売上比率、localization、規制、競争、unit economicsの地域差を確認する。

---

## Task 2：財務拼図とvaluation

- `subject`: `{会社名}の財務dataを復元し、複数方法でvaluationを行う`
- `activeForm`: `{会社名}の財務とvaluationを分析中`

### 1. 情報源matrix

| 優先度 | 種類 | 例 | 信頼度 |
|---:|---|---|---|
| 1 | IPO filing・規制文書 | SEC、HKEX、各国規制当局のdraft・filing | 🟢 |
| 2 | 親会社・関連公開企業の開示 | 持分法、関連当事者、segment開示 | 🟢 |
| 3 | 規制処分・compliance文書 | 中央銀行、competition authority、data regulator | 🟢 |
| 4 | bond・ABS・credit資料 | prospectus、rating report | 🟢～🟡 |
| 5 | corporate registry | 登記、資本金、子会社 | 🟡。制度と更新時期を確認 |
| 6 | 資金調達の公表・報道 | 金額、valuation、investor | 🟡 |
| 7 | 調査会社・証券会社 | industry report、peer data | 🟡 |
| 8 | 信頼できる報道 | Reuters、Bloomberg、The Information、LatePost、36Krなど | 🟡 |
| 9 | industry dataからの逆算 | market size × share | 🔴 |
| 10 | 匿名投稿 | 公開forumなど | 🔴。主要根拠にしない |

非公開資料、漏えい資料、認証回避、閉鎖group、個人情報を取得してはならない。

### 2. 財務data

各data pointに情報源、年月、通貨、単位、信頼度、計算方法を付ける。

- 売上高：3年のannual・quarterly range、business line、数量×単価、seasonality。
- cost：gross margin、R&D、sales、G&A。employee count × compensationなどの逆算はrangeで示す。
- profit：operating income、EBITDA、net income、adjusted income。調整項目を明示する。
- cash flow：営業cash flowの正負、capital expenditure、FCF、cash balance、burn rate、runway。
- efficiency：employee当たり売上高・利益、調達資本当たり売上高、公開peerとの比較。

### 3. cross-check

| 指標 | source A | source B | source C | 差異 | 採用range・理由 |
|---|---|---|---|---:|---|

同じ指標を異なる方法で推定し、収束しない場合は一点値を出さない。単一情報源は`[単一情報源]`とする。

### 4. 資金調達履歴

| round | 日付 | 調達額 | pre-money | post-money | lead | follow-on | 証券・権利 | 備考 |
|---|---|---:|---:|---:|---|---|---|---|

- valuation curve、調達間隔、down round、既存investorのfollow-on。
- liquidation preference、participation、anti-dilution、redemption、IPO covenantは公表資料で確認できる範囲だけ記載する。
- 条件が非公開なら、一般的な条件を当該roundの事実として推定しない。

### 5. valuationを複数方法で確認する

#### 最近の資金調達

- roundの日付、headline valuation、security class。
- preferred rightsとmarket変化を反映した普通株相当価値。20～40%など固定discountを機械的に使わず、理由を示す。
- strategic investorのpremium可能性。

#### 公開peer

3～5社を選び、理由を示す。

| peer | PSR | PER | EV/EBITDA | EV/Revenue | growth | margin | business mix |
|---|---:|---:|---:|---:|---:|---:|---|

liquidity、scale、growth、regulation、governance、security rightsの差を調整する。

#### DCF scenario

| 仮定 | 悲観 | 基準 | 楽観 | 根拠 |
|---|---:|---:|---:|---|
| 5年売上高CAGR | | | | |
| terminal operating margin | | | | |
| terminal growth | | | | |
| discount rate | | | | |
| terminal multiple | | | | |

assumptionを空想で埋めず、peer、unit economics、industry maturityに結びつける。

#### terminal outcomeからの逆算

5年・10年後のshare、売上高、margin、multipleから現在価値と年率return rangeを逆算する。

#### transaction comparison

直近2～3年の類似M&A・資金調達を比較し、control premium、market condition、strategic premiumを説明する。

### 6. 統合

| 方法 | 価値range | 信頼度 | 主要な弱点 |
|---|---:|---|---|

根拠のないweightで一つの加重値へ収束させない。方法間の差が大きい理由を説明し、保守range、基準range、楽観rangeを分ける。

---

## Task 3：industry structureと競合

- `subject`: `{会社名}のindustry structure、競合、代替を分析する`
- `activeForm`: `{会社名}の競争環境を分析中`

### 1. 市場定義

- 会社の自己定義とは独立にcore marketを定義する。
- TAM、SAM、SOMの対象、地域、年、通貨を示す。
- 複数調査の市場規模差を比較する。
- penetrationとindustry stage。
- growth driverと阻害要因。

### 2. value chain

```text
upstream supplier（集中度・交渉力）
    ↓
対象企業の工程（利益pool・差別化）
    ↓
downstream customer（集中度・代替）
    ↕
direct competitor / substitute / potential entrant
```

利益pool、single supplier・customer依存、構造変化を示す。

### 3. Porterの5 forces

| force | ★1～5 | 根拠 | 対象企業への影響 |
|---|:---:|---|---|
| 既存競争 | | | |
| 新規参入 | | | |
| 代替 | | | |
| supplier | | | |
| buyer | | | |

### 4. 競合map

| 競合 | 種類 | share推定 | 売上高 | valuation・時価総額 | 強み | 弱み | threat |
|---|---|---:|---:|---:|---|---|---|

直接競合、cross-industry、big-tech参入、異なるtechnology routeを含める。

### 5. 詳細比較

| 指標 | 対象企業 | competitor A | B | C |
|---|---:|---:|---:|---:|
| 設立年 | | | | |
| MAU等 | | | | |
| 売上高・成長 | | | | |
| 調達額・時価総額 | | | | |
| valuation / revenue | | | | |
| ARPU | | | | |
| gross margin | | | | |
| profitability | | | | |
| employee | | | | |
| technology | | | | |
| differentiation | | | | |
| internationalization | | | | |

### 6. 直近12か月の変化

資金調達、M&A、product、人事、採用、patent、technology、regulationを時系列で示す。

### 7. scenario

- 対象企業が優位を確立する条件。
- 複数社が共存する条件。
- 代替・競合に破壊される経路。

主観確率を精密値として示さず、triggerと方向を示す。

### 8. 世界の類似例

| peer | 発展経路 | 現在valuation | 類似段階からIPOまで | IPO後 | 成否要因 | 適用限界 |
|---|---|---:|---:|---:|---|---|

地域、regulation、顧客習慣の違いを明記する。

---

## Task 4：risk、governance、経営陣、exit

- `subject`: `{会社名}の全risk、経営陣、governance、exitを評価する`
- `activeForm`: `{会社名}のriskとgovernanceを分析中`

### 1. 創業者・CEO

- 経歴、連続起業、industry experience、過去に管理した規模。
- 直近3年の公開発言と実績。

| 発言日 | 判断・約束 | 対象期間 | 実績 | 判定 | source |
|---|---|---|---|---|---|

- 顧客、従業員、社会、短期利益と長期価値のtrade-off。
- 危機、layoff、規制、利益相反への対応。
- 公開された争点を、事実と疑惑に分ける。
- 総合評価★1～5。人格を推測せず、確認可能な行動で評価する。

### 2. core team

| 氏名 | 役割 | 経歴 | tenure | 主な責任 |
|---|---|---|---|---|

- 直近2年の重要な加入・退職。理由は公表または複数sourceで確認できる場合だけ示す。
- teamの補完性、欠けている能力、key person risk。
- Glassdoorなどの公開reviewはtrendとsample biasを示す。

### 3. ownershipとgovernance

| shareholder | 経済的持分 | 議決権 | security class | 基準日 | source |
|---|---:|---:|---|---|---|

- dual-class、VIE、shareholder agreement、一致行動。
- dilutionとemployee equity plan。
- board構成、investor seat、independent member。
- 関連当事者取引、同業競争、majority-minority conflict。

### 4. investor base

| investor | round | 金額 | 推定持分 | 種類 | strategic value | exit pressure |
|---|---|---:|---:|---|---|---|

fund life、secondary sale、follow-on、covenantは公開情報で確認できる範囲だけ扱う。既存investorがfollowしなかったことを、理由不明のまま否定signalと断定しない。

### 5. risk matrix

| 種類 | 具体的risk | 可能性 | 影響 | 重大度 | mitigation | monitor |
|---|---|---|---|---|---|---|
| regulation | competition、data、license | | | | | |
| competition | big-tech、price war、substitute | | | | | |
| technology | route failure、platform shift | | | | | |
| talent | founder・core team | | | | | |
| financing | runway、down round、covenant | | | | | |
| IPO | eligibility、market window | | | | | |
| geopolitics | export、cross-border data | | | | | |
| monetization | unit economics、user backlash | | | | | |
| governance | related party、opacity | | | | | |
| compliance | privacy、content、labor | | | | | |
| macro | rates、demand、capital market | | | | | |
| ESG | environmental・social・governance | | | | | |

### 6. exit scenario

| 方法 | 相対的可能性 | 時期range | value range | 条件 | 障害 |
|---|---|---|---:|---|---|
| 国内IPO | | | | | |
| HKEX IPO | | | | | |
| US IPO | | | | | |
| M&A | | | | | |
| 合法なsecondary transfer | | | | | |
| SPAC | | | | | |
| 長期非上場 | | | | | |

法令、transfer restriction、lock-up、investor eligibilityを確認する。非公開marketへのアクセスを手配しない。

### 7. 逆向き思考

- 最も現実的な失敗経路を3件。
- trigger、回収可能価値、liquidation waterfall。
- 合理的な投資家が参加しない理由を5件以上。
- 類似企業の失敗例。
- 仮説を撤回するsignal。

---

## Task 5：technology、IP、R&D

- `subject`: `{会社名}のtechnology stack、patent、R&D能力を分析する`
- `activeForm`: `{会社名}のtechnologyとIPを分析中`

### 1. technology stack

公開されたtechnical blog、conference、open source、job descriptionから推定する。security上の非公開構成や個人情報を探索しない。

- architectureと選択理由。
- migration・rebuild求人、outage、bugなどのtechnical debt signal。
- platform、cloud、chip、OSへの依存。

### 2. patent

Google Patents、CNIPA、USPTOなど公開databaseを使う。

| 指標 | 数値 | 基準日 | source |
|---|---:|---|---|
| granted patent | | | |
| pending application | | | |
| 直近2年の出願 | | | |
| 領域別構成 | | | |
| citation | | | |
| 国際family | | | |

patent数ではなく、claimの広さ、事業との関連、citation、litigation、残存期間を確認する。

### 3. R&D

- researcher・engineer数と比率。LinkedIn・求人からの推定はrangeにする。
- compensation、infrastructureを含むR&D費用range。
- paper、conference、GitHub、technical blog。
- researchからproductまでの速度とcommercialization。

### 4. talent

| 氏名 | 役割 | 専門 | 前職・研究機関 | 公開された成果 |
|---|---|---|---|---|

採用動向、報酬range、重要な退職は、公開情報とprivacyを尊重して扱う。

### 5. technology moat

| 要素 | ★1～5 | 証拠 | 持続性 |
|---|:---:|---|---|
| algorithm・model | | | |
| data | | | |
| engineering | | | |
| talent | | | |
| ecosystem・standard | | | |

AIその他の新技術が、enhancement、substitute、neutralのどれかを事業別に評価する。Web3、AR/VR、quantumなど、対象事業への具体的な経路がないthemeは無理に含めない。

### 6. AI・新技術の影響

- AI、open source、AR/VR、Web3、quantum computingなどの新技術について、対象企業の事業へ具体的な影響経路があるものだけを扱う。
- 影響をenhancement、substitute、neutralのいずれかへ分類し、product、cost、distribution、競争優位のどこへ作用するかを示す。
- 技術の話題性ではなく、顧客価値、売上高、margin、capital expenditureへ結びつく証拠を確認する。
- 新技術が既存のtechnology moatを強化する条件と、無効化する条件を分ける。

### 7. technology risk

| risk | 内容 | 可能性 | 影響 | 先行signal |
|---|---|---|---|---|
| route failure | | | | |
| open-source substitute | | | | |
| platform dependence | | | | |
| security・privacy | | | | |
| key talent | | | | |

---

## Task 6：公開alternative data

- `subject`: `{会社名}の公開alternative dataと異常signalを分析する`
- `activeForm`: `{会社名}のalternative dataを分析中`

alternative dataは補助証拠である。利用規約、robots、privacy、access controlを守り、login回避、閉鎖community、漏えいdata、個人追跡を行わない。

### 1. 求人

LinkedIn、Indeed、Glassdoor、企業career page、公開求人siteを使う。

- 公開求人数と6か月trend。
- competitorとの比較。

| 種類 | 件数・range | 比率 | signal |
|---|---:|---:|---|
| engineering・R&D | | | |
| product | | | |
| sales・BD | | | |
| marketing・operation | | | |
| data・AI | | | |
| international | | | |
| compliance・legal | | | |
| finance・IR | | | |

IR求人だけでIPO確定とせず、IPO準備の可能性として扱う。

### 2. product data

App Store、Google Play、七麦、SimilarWebなど、合法的に利用可能な公開dataを使う。

| 指標 | data | source | trend | limitation |
|---|---|---|---|---|
| ranking | | | | |
| rating | | | | |
| review count | | | | |
| download estimate | | | | |
| update frequency | | | | |
| web traffic | | | | |

reviewの頻出論点を要約し、bot、campaign、selection biasを確認する。

### 3. 公開sentiment

公式accountと公開されたX、Reddit、微博、知乎、小紅書などを調べる。匿名投稿は事実の根拠にせず、sentiment signalとして扱う。個人を特定・追跡しない。

### 4. corporate registry・legal

利用可能な公開registry、裁判・行政database、企業開示を使う。

- capital、shareholder、subsidiary、business scope、trademarkの変更。
- litigation、IP dispute、labor、administrative penalty、enforcement。
- 重大案件の当事者、日付、手続状態、金額、潜在影響。

| 種類 | 件数 | 重要案件 | 状態 | source |
|---|---:|---|---|---|

### 5. supply chain・partner

公開されたsupplier、customer、partnership、government procurement、tenderを確認し、counterparty側の開示でcross-checkする。

### 6. digital footprint

公開されたdomain、certificate transparency、trademarkなどを、security・privacyを侵害しない範囲で調べる。新domainやsubdomainだけで未公表productを断定しない。

### 7. industry exposure

conference、standardization、award、government・associationとの公開interactionを調べる。awardやunicorn listは事業品質の証拠として過大評価しない。

### 8. secondary transaction

合法的かつ公開されたsecondary platformや会社承認済みtransactionのindicative priceを調べる。private group、無許可仲介、規制対象者以外への勧誘を扱わない。

- indicative valuationと最新roundの差。
- bid・ask、取引成立の有無、security class。
- employee saleに関する集計情報が公表されている場合だけ扱う。

### 9. signal score

| category | positive / negative / neutral | strength | confidence | finding |
|---|---|---|---|---|
| hiring | | | | |
| product | | | | |
| sentiment | | | | |
| legal | | | | |
| supply chain | | | | |
| digital footprint | | | | |
| industry exposure | | | | |
| secondary | | | | |

### 10. 異常signal一覧

通常の事業説明と整合しないsignalを、重要度順に列挙する。

- 売上高・user成長の説明と逆方向の採用縮小、product ranking低下、supplier発言。
- 急な経営陣退職、法人・株主構成変更、訴訟・行政処分の増加。
- 最新roundのheadline valuationと公開secondary価格の大幅な乖離。
- 会社が説明するtechnology優位と、patent、technical hiring、product updateの不一致。
- 単一signalで断定せず、複数sourceと時間軸で確認する。説明できない場合は「未解決の異常signal」とする。

---

## 手順4：6 Agentを同時に起動する

AgentまたはTaskツールを**同一メッセージで6回並行呼び出し**する。

- `subagent_type`: `general-purpose`
- `run_in_background`: `true`
- `team_name`: 作成済みteam
- `name`: 各role名

共通prompt：

```text
あなたは{会社名}の非上場企業調査teamに所属する{役割名}である。

Task：{subject}
要件：{description}

非上場企業の調査規則：
- 標準化された財務開示がないため、複数の公開情報源を組み合わせる。
- dataが不足または矛盾する場合、推定で隠さず信頼度を付ける。
- 公開・合法・利用可能な情報だけを使い、access control、privacy、規制を回避しない。
- 情報が見つからないことと、事実が存在しないことを区別する。

検索：
- WebSearchで、会社名とrevenue、valuation、funding、users、IPO、filing、regulation、layoffなどを英語・中国語・現地語で検索する。
- 人物、競合、親会社、supplierの正式名称も使う。
- filing、規制文書、関連公開企業の年次報告書を優先する。
- WebFetchで重要記事と一次資料の本文を読み、検索snippetだけで結論を出さない。

記載規則：
- 重要dataへsource、年月、通貨、単位、信頼度を付ける。
- 重要dataは原則として2情報源でcross-checkする。
- conflicting dataはすべて示し、採用理由を説明する。
- 事実、会社説明、第三者推計、自分の推定を区別する。
- 推定は式、入力値、rangeを示す。
- data不足は明記し、捏造しない。
- 最終報告は自然な日本語とする。

出力：
1. Markdown表を含む完全な分析。
2. 各sectionの結論と★1～5評価。
3. 本観点の総合評価と情報充足度。
4. 最重要の発見3件。
5. 結論を最も左右する情報blind spot。
6. TaskUpdateでcompletedにし、SendMessageでteam-leadへ完全な報告を送る。
```

## 手順5：進捗を共有する

各Agentの状態を表で示す。報告受領ごとに重要な発見を3～5点共有し、6件すべてを受領する。同じTaskを重複起動しない。

## 手順6：cross-validationと情報拼図

### 1. data conflict

複数Agentが扱った同じdataを比較し、source、定義、期間、通貨、security classの違いを解決する。解決しない場合はrangeとする。

### 2. signal consistency

- 売上高・顧客成長と採用trend。
- technology narrativeとpatent・talent・product evidence。
- valuationと競争上の位置。
- 経営陣の説明と実際の資本配分・公開signal。
- cash runwayと採用・投資計画。

### 3. white・gray・black area

- **white**：複数sourceで確認した事実。
- **gray**：一部証拠があるが確定できない。
- **black**：重要だが確認できない。

### 4. bias check

positive evidenceだけが詳細でないか、negative evidenceを同じ強度で探索したか、企業広報に依存していないか確認する。

## 手順7：最終報告

### 1. 結論

50～100字で、事業の質、価値range、最大のblind spot、判断の確度を先に示す。

### 2. 会社snapshot

| 項目 | 内容 | 基準日 | 信頼度 |
|---|---|---|---|
| 正式名称・所在地 | | | |
| 設立・創業者・CEO | | | |
| core business | | | |
| employee range | | | |
| 最新round・headline valuation | | | |
| 売上高・profit range | | | |
| user・customer range | | | |
| investor | | | |
| legal・ownership structure | | | |

### 3. 6観点のscorecard

| 観点 | role | ★1～5 | 中核判断 | 信頼度 | 情報充足度 |
|---|---|:---:|---|---|---|

scoreの単純平均を内在価値と混同しない。

### 4. cross-checked data

| 指標 | data・range | source数 | source | 信頼度 | 注記 |
|---|---|---:|---|---|---|

### 5. consistency matrix

| 検査 | signal A | signal B | 一致 / 矛盾 / 不明 | 解釈 |
|---|---|---|---|---|

### 6. 観点別の重要発見

各観点3～5点。sourceと信頼度を付ける。

### 7. 事業価値

- 事業の本質と予測可能性。
- moat scorecard。
- 資金調達調整、peer、DCF、terminal outcome、transaction comparisonのvalue range。

| 方法 | value range | 通貨・基準日 | 信頼度 | limitation |
|---|---:|---|---|---|

**統合range**：保守 / 基準 / 楽観。現在のheadline valuationおよび普通株相当価値と比較し、安全余裕またはovervaluation rangeを示す。情報不足なら「信頼できるvaluationを提示できない」と明記する。

### 8. 強気論と弱気論

各5～7点を、証拠と反証条件付きで示す。どちらが強いかを、情報品質も含めて判断する。

### 9. risk matrix

Top 3のrisk、trigger、monitor、mitigationを示す。

### 10. exit

最も現実的なexit、時期range、条件、障害を示す。exitなしのscenarioも含める。

### 11. decision memo

```text
会社：
最新round・valuation：
stage：seed / growth / mature / pre-IPO
情報充足度：

中核仮説：
1.
2.
3.

value range：
現在valuationとの比較：

検証すべき仮定：
- 仮定 → 指標 → trigger → 時期

仮説を撤回する条件：
-

調査上の判断：深掘り / watchlist / 現時点では見送り / 判定不能
再評価条件：
想定exit：
期間range：
```

具体的な投資参加、private share取得、仲介、適格性判断は行わない。投資家類型別の論点を示す場合も、法的・流動性・情報riskを明記する。

### 12. blind spot map

| 観点 | 既知 | 不明 | 影響 | 確認方法 |
|---|---|---|---|---|

### 13. monitoring

| 項目 | 頻度 | 公開source | 指標 | 警戒条件 |
|---|---|---|---|---|

### 14. 総括

150～250字で、事業の本質、value range、最大の確実性・不確実性、次の確認事項をまとめる。

### 手順8：保存する

`reports/{会社名}/{会社名}-private-{YYYYMMDD}.md`へ保存する。

### 手順9：teamを終了する

全報告受領後、各Agentへ`shutdown_request`を送り、TeamDeleteで資源を整理する。

---

## 重要原則

1. 6 Agentを同一メッセージで並行起動する。
2. 各重要dataへsource、年月、通貨、単位、信頼度を付ける。
3. 推定は式、入力、range、弱点を示す。
4. 重要dataは原則として2情報源でcross-checkする。
5. 観点間のsignal consistencyを必ず確認する。
6. 結論を明確にするが、情報不足なら判定不能とする。
7. 長時間の無言を避け、完了した部分を簡潔に共有する。
8. 英語・中国語・現地語で検索しても、最終出力は日本語にする。
9. 資料量と事業品質を混同しない。
10. 情報blind spotを残し、もっともらしい推測で埋めない。
11. alternative dataは補助証拠であり、privacy・access control・法令を守る。
12. headline valuationではなく、security rightsと事業価値を区別する。
13. 本資料は調査・学習用であり、投資助言ではない。
