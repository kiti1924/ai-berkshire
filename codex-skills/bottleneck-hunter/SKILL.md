---
name: bottleneck-hunter
description: "AI Berkshire Skill: supply chain bottleneck探索：世界の産業chainにある制約を投資調査へつなげる（原本: skills/bottleneck-hunter.md）"
---

## Codexアダプター注記

このSkillは`skills/bottleneck-hunter.md`から生成され、Claude CodeとCodexで同じ正本のワークフローを共有する。

- `$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う。
- Windows環境のPowerShellでファイル（SKILL.mdや参照資料）を読み取るコマンドを実行する際は、文字化け（CP932/Unicode誤認識）を防ぐため、必ず `Get-Content -Encoding utf8 -Raw <ファイルパス>` または `python -c "import pathlib; print(pathlib.Path(r'<ファイルパス>').read_text(encoding='utf-8'))"` を使用すること。
- 正本がTask、Agent、WebSearch、Bash、Read、WriteなどClaude Code固有の機能を参照する場合は、このセッションで利用できる最も近いCodex機能へ置き換える。必要に応じてサブエージェント、Web検索、ローカルツール実行用のシェルコマンド、ワークスペース内の通常のファイル編集を使う。
- 共通ツールは本リポジトリの`tools/`から使用する。`~/ai-berkshire/tools/...`を参照するコマンドは、リポジトリを`~/ai-berkshire`へチェックアウトした前提である。必要なら現在のワークスペースのパスを優先する。
- `AGENTS.md`の調査品質規則を維持する。財務データを照合し、評価と計算には精密計算ツールを使い、不確実性と情報源の不足を明示する。

# supply chain bottleneck探索：世界の産業chainにある制約を投資調査へつなげる

$ARGUMENTS のmega trendについて、supply chainのbottleneckを調べ、投資候補を抽出する。

## 中核となる考え方

「AIが推薦する銘柄は何か」ではなく、**このtrendが拡大し続けた場合、どの物理的な工程が最初に不足するか**を問う。

通常の企業調査は、完成品のleaderや既知の成長市場へ集中しやすい。本Skillは逆に、supply chainの物理的な制約から始める。注目度は低くても、供給が止まればindustry全体が待たざるを得ない部品、材料、装置、infrastructureを探す。

第1層の制約であるGPU、HBM、電力などは既に広く認識されている場合がある。追加的な調査価値は、第2・第3層の光module、laser、InP substrate、SOI wafer、epitaxy equipment、wafer-level testing、IC substrate、特殊glass fiberなどに残る可能性がある。ただし、注目度が低いこと自体を割安性とみなさない。

---

## 手順1：mega trendを確認する

### 1.1 選定基準

短期的なthemeではなく、原則として次をすべて満たすtrendを対象とする。

| 基準 | 要件 | 検証方法 |
|---|---|---|
| 継続性 | 3～5年以上の需要拡大を裏づける事実または複数scenarioがある | 業界予測、企業のcapital expenditure計画、政策を確認する |
| 物理性 | 実際のhardware、material、equipment、建設を必要とする | software更新だけか、物理的増設を伴うかを分ける |
| 規模 | 世界の年間capital expenditureが500億USD超を一つの目安とする | 主要企業のguidanceと公的統計を集計する |
| 加速性 | 需要増加が供給能力の増加を上回る可能性がある | 需要成長率と能力増強計画を比較する |

数値には基準年、通貨、情報源を付ける。500億USDは機械的な合否基準ではなく、産業規模に応じて理由を示して調整できる。

### 1.2 初期監視theme

実行時にWebSearchと一次資料を使って最新状況を確認する。初期候補は次のとおりである。

1. **AI infrastructure**：data center、accelerator cluster、network interconnect、電力。
2. **energy transition**：原子力発電の再評価、送配電網、energy storage。
3. **defense modernization**：国防支出cycle、供給網再編。
4. **semiconductor reindustrialization**：米国・欧州・日本などの製造投資、装置・材料制約。
5. **space economy**：satellite internet、launch cadenceの増加。

ユーザーが特定themeを指定した場合は、そのthemeだけを扱う。

### 1.3 trend確認の出力

```text
trend名：
中核driver：{一文}
確認済み事象（少なくとも3件）：
  1. [日付] [事象] [情報源]
  2.
  3.
年間capital expenditure：世界で約{金額・通貨・基準年}、成長率{割合}
需給判断：需要増加率 > 供給能力増加率 / 逆 / 判定不能
結論：✅ 継続調査 / ❌ 証拠不足 / ❓ 条件付き
主な反証条件：
```

---

## 手順2：物理的なsupply chainへ分解する

### 2.1 layer構造

概念名だけで止めず、実在する物、工程、設備、認証まで分解する。

```text
Layer 0（end use）：最終製品・service
    │
Layer 1（中核component）：市場で広く認識された主要hardware
    │                 ↑ 注目度が高く、期待が価格へ反映済みの可能性
    ├────────────────
    │                 ↓ 相対的に注目度が低い探索領域
    │
Layer 2（subcomponent・material）：中核componentを支える部品・材料
    │
Layer 3（upstream equipment・raw material）：製造装置と原材料
    │
Layer 4（infrastructure）：電力、冷却、土地、人材、license、certification
```

### 2.2 AI infrastructureの分解例

```text
Layer 0：AI modelのtraining・inference service
Layer 1：GPU・accelerator、HBM、server、data center
Layer 2：
  ├─ interconnect：optical module、fiber、switch chip、copper cable
  ├─ optical core：EML・VCSEL・CW laser、modulator、photodetector
  ├─ semiconductor material：InP、GaAs、SOI、SiC substrate
  ├─ advanced packaging：CoWoS関連、HBM TSV、ABF film
  ├─ PCB・substrate：high-speed PCB、IC substrate、特殊glass cloth
  ├─ testing：probe card、burn-in、ATE
  ├─ thermal management：liquid cooling、CDU、immersion coolant
  └─ power distribution：busway、UPS、switchgear、transformer
Layer 3：
  ├─ epitaxy equipment：MOCVD、MBE
  ├─ lithography・etch：special wavelength lithography、InP etch
  ├─ raw material：high-purity indium、gallium、germanium、specialty gas、target
  └─ certification・standard：MSA、Telcordia
Layer 4：
  ├─ electricity：nuclear、gas generation、transmission
  ├─ cooling water・heat rejection infrastructure
  └─ data center site・permit
```

### 2.3 他themeの探索語

各themeについて同じ水準まで分解し、必要に応じて次の英語検索語を使う。これらは検索用の原語であり、最終説明は日本語にする。

- `"{theme}" supply chain bottleneck {year}`
- `"{theme}" shortage critical component`
- `"{theme}" capacity constraint`
- `"{theme}" sole source supplier`

日本、中国、韓国、台湾などのsupplierを調べる際は、現地語の正式名称と検索語も併用する。

---

## 手順3：bottleneckを判定する

### 3.1 6基準

Layer 2～3の各工程を次で評価する。

| # | 基準 | 問い | signal |
|---|---|---|---|
| 1 | **供給集中度** | 世界の有効supplierは何社か | 🔴 2社以下 / 🟡 3～5社 / 🟢 6社以上 |
| 2 | **能力増強期間** | 新規能力が量産可能になるまで何年か | 🔴 2年超 / 🟡 1～2年 / 🟢 1年未満 |
| 3 | **代替困難性** | 別技術・material・supplierへ切り替えられるか | 🔴 困難 / 🟡 一部可能 / 🟢 容易 |
| 4 | **capacity utilization** | 現在の利用率はどの程度か | 🔴 90%超 / 🟡 70～90% / 🟢 70%未満 |
| 5 | **需要成長** | downstream需要の年成長率はどの程度か | 🔴 50%超 / 🟡 20～50% / 🟢 20%未満 |
| 6 | **顧客認証期間** | 新supplierが量産承認を得るまでどの程度か | 🔴 1年超 / 🟡 6～12か月 / 🟢 6か月未満 |

各判定に情報源と基準日を付け、公開データがない場合は「不明」とする。推定を事実として点数化しない。

**bottleneck区分**：

- 🔴が4項目以上：**S**。single point of failureに近い。
- 🔴が3項目：**A**。重大な供給制約。
- 🔴が1～2項目：**B**。圧力はあるが、解消経路が存在する。
- 🔴なし：現時点ではbottleneckとして扱わない。

### 3.2 mapの出力

```text
supply chain bottleneck map — {trend名}
更新日：YYYY-MM-DD
データ基準日：YYYY-MM-DD

S（single point of failure）：
  1. [工程] — [制約の理由] — supplier：[企業]

A（重大な制約）：
  1.

B（一定の圧力）：
  1.

前回からの変化：
  - [新規 / 格上げ / 格下げ / 解消] [工程] — [根拠]

情報不足：
```

---

## 手順4：bottleneckから上場企業を抽出する

### 4.1 S・A区分の関連企業を調べる

WebSearchを使い、次の検索語を市場・言語ごとに組み合わせる。

- `"{工程}" supplier listed company`
- `"{製品}" manufacturer stock`
- `"{製品}" market share company`

上場企業だけでなく、重要な非上場supplierも記録し、直接投資可能性とは分ける。

### 4.2 初期screening

| 基準 | 目安 | 理由 |
|---|---|---|
| 上場 | 中国本土、香港、米国、日本、台湾、欧州など | 直接取得可能性を確認する |
| 関連売上比率 | 30%超を優先 | themeへの収益感応度を確認する |
| 時価総額 | 100億USD未満を優先するが、大型企業を自動除外しない | 期待の織込み度を確認する |
| 流動性 | 日次売買代金100万USD超を参考とする | 実際の市場流動性を確認する |

関連売上比率や流動性が不明なら、推定で通過させず「要確認」とする。

### 4.2.1 valuation確認

**bottleneckが実在しても、現在価格が魅力的とは限らない。** 各企業のPSR、PER、時価総額、TAM、成長率を計算し、通貨と基準日を付ける。

#### red signal

いずれかに該当する場合、調査優先度は原則として★★を上限とし、「valuationに重大な懸念」と明記する。ただし閾値の意味を業種に応じて説明する。

1. **時価総額 > 当該企業が現実に獲得可能なTAMの20%**。TAMの通貨、年、対象範囲を確認する。
2. **PSR > 30倍かつ売上高成長率 < 100%**。100%超でも高成長継続が必要と警告する。
3. **時価総額 > 5年後の楽観売上高予想の10倍**。
4. **増資後60日以内に株価が2倍**。sentiment要因を確認し、signalを1段階下げる。

#### yellow signal

1. **赤字かつPSR > 15倍**：収益化経路、必要資金、達成時期を示す。
2. **PSRが黒字同業の5倍超**：share、成長率、堀の差でpremiumを説明できるか確認する。
3. **PER > 80倍**：PEGだけで正当化せず、利益成長の持続性とdownsideを計算する。

#### green signal

- PSR < 10倍で売上高が成長している。
- PER < 30倍で、持続的な堀とcash conversionを確認できる。

#### 10年return test

各社について次に答える。

> 現在の時価総額で取得し、楽観scenarioが実現し、10年後にPER 25倍で評価される場合、年率returnはいくらか。

年率10%未満なら「現在価格では安全余裕が乏しい」とする。利益率、希薄化、net cash、税、退出PERの仮定を明記する。

この検査は、早期企業を一律に除外するためではない。高valuationを支える成長、TAM、競争優位、資金需要を具体的に検証するためのものである。

### 4.3 企業別template

```markdown
## {会社名}（{ticker}）

### bottleneck上の位置
- supply chain上の工程：
- market share：世界{順位・割合・基準日}
- 確認済み顧客：

### capacity
- 現在能力・利用率：
- 増強計画・稼働予定：
- 必要資金と手元資金：

### 財務snapshot
- 時価総額 / 売上高 / 利益 / 成長率：
- 関連事業売上比率：
- 売上総利益率の推移：
- PSR / PER / FCF Yield：

### risk
- [ ] 代替技術
- [ ] 増資・転換社債・株式報酬による希薄化
- [ ] 地政学・輸出管理
- [ ] 経営陣・governance
- [ ] 顧客集中
- [ ] valuationへの過度な期待織込み

### bottleneckの持続性
- 解消時期のscenario：
- 解消後に残る競争優位：
- 一時的制約か構造的制約か：
```

---

## 手順5：storyをcross-checkする

### 5.1 順方向

| 確認事項 | 問い | 主な情報源 |
|---|---|---|
| 顧客 | 主要顧客が採用・契約を確認しているか | 企業開示、顧客側決算、規制開示 |
| 売上高 | 制約が売上高成長へ現れているか | 直近2～3四半期の決算 |
| 価格 | 製品価格またはcontract priceが上昇しているか | 契約、業界価格、決算説明 |
| capacity | lead time、backlog、利用率が制約を示すか | 企業開示、顧客発言、業界統計 |
| capital | 実際に能力増強へ資金を投じているか | capital expenditure guidance |

### 5.2 逆方向 — マンガー式の反証

| 問い | 検証するrisk |
|---|---|
| 合理的な投資家が買わない理由は何か | bearish case |
| 別の技術routeで回避できるか | technology substitution |
| 中国その他のsupplierが短期間で能力を増やせるか | supply shock |
| 最終需要が50%減速した場合にどうなるか | downside sensitivity |
| 経営陣は高値で希薄化した履歴があるか | capital allocation |
| 現在価格はどの成長率とmarginを前提にするか | valuation |

### 5.3 複数signal

- 同じ工程の複数企業で、注文、価格、売上高が同方向か。
- downstream顧客が供給制約を言及しているか。
- 業界団体、公的統計、独立調査に同じsignalがあるか。

重要結論は原則として2つ以上の独立した情報源で確認する。

---

## 手順6：bottleneck opportunity boardを作る

### 6.1 ranking

| 順位 | 会社 | ticker | 時価総額 | 年間売上高 | PSR | PER | 工程 | 区分 | share | 売上高成長率 | 調査signal | valuation |
|---:|---|---|---:|---:|---:|---:|---|---|---:|---:|---|---|
| 1 | | | | | | | | S/A | | | ★1～5 | 妥当 / 高い / 過度 |

**必須**：時価総額、年間売上高、PSR、PERを確認する。取得不能なら理由を示し、signalは★★を超えない。赤字企業ではPERを`N/M`とし、無理に数値を作らない。

調査signal：

- ★★★★★：顧客、売上高、capacity、複数情報源で確認し、valuationも妥当。
- ★★★★☆：多くを確認し、valuationはgreenまたは説明可能なyellow。
- ★★★☆☆：論理は成立するが未確認点があり、yellow signalを許容できる。
- ★★☆☆☆：初期signal、またはbottleneckは実在するがvaluationがred。
- ★☆☆☆☆：概念段階で、実需・企業収益との接続を確認できない。

### 6.2 1ページ要約

```text
{会社名}（{ticker}）— {bottleneck上の一文}

なぜ制約か：
{2～3文}

なぜこの会社か：
{2～3文}

catalyst：
- 1～3か月：
- 3～12か月：

主要risk：
1.
2.

重要数値：時価総額 / 年間売上高 / PSR / PER / 売上高成長率 / 関連売上比率

安全余裕test：現在価値、10年後PER 25倍、必要純利益・売上高、年率return、仮定

検証状態：✅ 顧客 / ✅ 売上高 / ✅ valuation / ⚠️ valuation高い / ❌ 未確認

結論：深掘り / watchlist / 現時点では追跡しない
```

### 6.3 次の対応

| 対象 | 対応 | 理由 |
|---|---|---|
| A | `/investment-team`で深掘り | S区分かつ複数検証済み |
| B | watchlistへ追加し、次回決算を待つ | 収益への反映が未確認 |
| C | 現時点では追跡しない | 代替技術またはvaluation riskが大きい |

---

## 手順7：mapを継続更新する

### 7.1 増分確認

1. 既存bottleneckが継続しているか。
   - 新supplierの参入。
   - capacity増強。
   - 代替技術。
2. 新たな制約を探索する。
   - 直近7日の`shortage`、`capacity constraint`、`lead time`など。
   - 決算資料のsupply chain disclosure。
3. S/A/Bの格上げ、格下げ、解消を記録する。

### 7.2 状態ファイル

`reports/bottleneck-map/`に次を維持する。

- `master-map.md`：全体map。
- `watchlist.md`：監視対象。
- `YYYY-MM-DD/`：日次の探索報告。
- `deep-dive/`：企業別の深掘り。

既存履歴を上書きせず、変更理由を追記する。

---

## 1時間ごとの定期探索mode

定期taskでは、少なくとも1時間間隔とし、**重要な新情報がある場合だけ報告する**。

### 探索工程

1. WebSearchで直近1～2時間のsupply chain newsを確認する。
   - 英語検索語：`supply chain bottleneck`, `shortage`, `capacity constraint`, `allocation`, `lead time`, `sole source`
   - 中国語検索語：`瓶颈`, `缺货`, `产能`, `涨价`
2. watchlist企業の異常な価格変動。5%超を一つの参考とする。
3. 決算、法定開示、重要発表。
4. valuationが事前条件へ入ったか。
5. 新規制約、具体的な企業機会、重大な状態変化があれば報告する。なければ通知用の報告は作らず、実行logへ「新signalなし」と記録する。

### 保存規則

`reports/bottleneck-map/YYYY-MM-DD/`

| 状況 | ファイル名 | 例 |
|---|---|---|
| 明確な候補あり | `HH-MM-{ticker1}-{ticker2}.md` | `09-00-FORM-IBDN.md` |
| signalのみ | `HH-MM-signal-scan.md` | `14-00-signal-scan.md` |
| 新規情報なし | ファイルを作らない | — |

ファイル名へ含めるtickerは、valuation確認を通過し、深掘り対象となった企業だけとする。

### 候補ありtemplate

```markdown
# bottleneck探索 — YYYY-MM-DD HH:MM

## 明確な候補

### {会社名}（{ticker}）— {位置づけ}

**今回のtrigger**：{事象・数値}

**bottleneck**：Layer {X}、{工程}、区分{S/A/B}
**財務snapshot**：時価総額 / 売上高 / PSR / PER / 成長率
**valuation signal**：red / yellow / green。理由を記載する
**安全余裕**：10年後PER 25倍scenarioの年率return

**強気論**：
1.
2.

**弱気論**：
1.
2.

**次の対応**：深掘り / watchlist / より良い価格を待つ

## その他のsignal

| 工程 | signal | 情報源 | 初期判断 |
|---|---|---|---|

## watchlist変更

{格上げ / 格下げ / 追加 / 削除 / 変更なし}
```

### signalのみtemplate

```markdown
# bottleneck signal scan — YYYY-MM-DD HH:MM

## 新signal

| 工程 | 内容 | 情報源 | 投資可能な企業 | 次の確認 |
|---|---|---|---|---|

## watchlist

{変更なし / 変更内容}
```

---

## AI調査のbias

| bias | 起こり方 | 対応 |
|---|---|---|
| 大型株bias | 検索結果が大型企業で占められる | `small cap`、専門supplier、現地語で追加検索する |
| 英語bias | 日本、韓国、台湾などを見落とす | 各市場と現地語でsupplierを探索する |
| narrative bias | `AI関連`というlabelだけで魅力的に見える | 物理的な工程、売上比率、顧客を確認する |
| confirmation bias | 制約を見つけた後に賛成証拠だけを集める | 手順5.2の反証を必ず行う |
| recency bias | 古いcapacity情報を現在も有効とみなす | 直近30日と最新決算を優先し、基準日を付ける |

---

## 最優先原則

1. **銘柄推薦よりsupply chain分解を優先する。**
2. **物理的制約を扱う。**
3. **第2・第3層を能動的に探す。**
4. **重要結論は2つ以上の独立情報源で確認する。**
5. **情報不足を推測で埋めない。**
6. **bottleneckには期限がある。解消時期を必ず考える。**
7. **小型企業であることを品質と混同しない。**
8. **bottleneckの実在と投資価値を分ける。高PSR、赤字、希薄化をstoryで正当化しない。**
9. **データから始め、強気・弱気双方を示す。**
10. **本資料は調査・学習用であり、投資助言ではない。**

---

## 出力要件

1. 保存先：
   - 完全scan：`reports/bottleneck-map/{trend}-bottleneck-{YYYYMMDD}.md`
   - 日次scan：`reports/bottleneck-map/daily/{YYYY-MM-DD}-{am/pm}.md`
   - 全体map：`reports/bottleneck-map/master-map.md`
   - watchlist：`reports/bottleneck-map/watchlist.md`
2. 最終出力は共通locale設定に従い、自然な日本語の「だ・である調」とする。
3. 結論を先に示し、不要な修辞を避ける。
4. 数値には情報源、通貨、単位、基準日を付け、推定は「推定」とする。
5. データ、因果、結論の順で示す。
6. 中核判断には反対証拠を併記する。
