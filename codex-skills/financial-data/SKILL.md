---
name: financial-data
description: "AI Berkshire Skill: 財務データ取得・クロスチェック規程（原本: skills/financial-data.md）"
---

## Codexアダプター注記

このSkillは`skills/financial-data.md`から生成され、Claude CodeとCodexで同じ正本のワークフローを共有する。

- `$ARGUMENTS`は、現在のCodexスレッドで受け取ったユーザーの依頼として扱う。
- 調査レポート等のファイル書き出し指示（例: `reports/{会社名}/...`）がある場合は、単に会話上にMarkdownを出力して終了せず、必ずファイル書き込みツールまたはシェルコマンド（`mkdir -p reports/{会社名}` および ファイル書き込み）を実行して実際にファイルとして保存すること。
- Claude Code固有の機能（Task, Agent等）は、このセッションで利用できる最も近いCodex機能（サブエージェント、Web検索、ローカルシェル等）へ置き換える。
- 共通ツールは本リポジトリの`tools/`（`python3 tools/...`）を使用し、`AGENTS.md`の調査品質規則（精密計算ツールでの検証、不確実性の明示等）を維持する。

# 財務データ取得・クロスチェック規程

本規程は、企業の財務データを扱うすべての調査に適用する。**重要データはそれぞれ2つの独立した情報源で確認し、差異が1%を超える場合は明示すること。**

---

## 情報源の優先順位

### 米国株（PDD、Tencent ADR、NetEase ADRなど）

| 優先順位 | 情報源 | URL | 取得方法 |
|---|---|---|---|
| 1（主） | **macrotrends** | macrotrends.net/stocks/charts/{ticker} | 登録不要で直接アクセス |
| 2（副） | **stockanalysis** | stockanalysis.com/stocks/{ticker}/financials | 登録不要で直接アクセス |
| 一次資料 | SEC EDGAR | sec.gov/cgi-bin/browse-edgar | 10-K / 10-Qの原文 |

### 香港株（Tencent 0700、NetEase 9999、Meituan 3690など）

| 優先順位 | 情報源 | URL | 取得方法 |
|---|---|---|---|
| 1（主） | **aastocks** | aastocks.com/tc/stocks/analysis/company-fundamental | 直接アクセス |
| 2（副） | **macrotrends**（ADR ticker） | TencentはTCEHY、NetEaseはNTES | 直接アクセス |
| 一次資料 | HKEXnews（披露易） | hkexnews.hk | 年次報告書PDF |

### 中国A株（37 Interactive Entertainment、G-bitsなど）

| 優先順位 | 情報源 | URL | 取得方法 |
|---|---|---|---|
| 1（主） | **Eastmoney（东方财富）** | eastmoney.com → 銘柄コードを検索 → 財務諸表 | 直接アクセス |
| 2（副） | **CNINFO（巨潮资讯）** | cninfo.com.cn | 年次報告書・四半期報告書の原文PDF |

---

## 実行手順

### 手順1：データを取得する

売上高、純利益、売上総利益率、営業キャッシュフロー、負債比率など、各財務指標について**情報源1**と**情報源2**から個別に数値を取得する。

### 手順2：差異率を計算し、判定する

```text
差異率 = |情報源1の数値 - 情報源2の数値| / |情報源1の数値| × 100%
```

| 差異率 | 対応 |
|---|---|
| ≤ 1% | ✅ 一致。情報源1の数値を採用し、両方の情報源を記載する |
| 1%超～5% | ⚠️ 「データに差異あり」と明記し、両方の数値と想定原因（為替・会計上の定義など）を示す |
| > 5% | ❌ 「データに重大な差異あり」と明記する。一次資料で確認するまで、そのまま使用してはならない |

分母が0または0に近い場合は差異率だけで判定せず、絶対差と指標の性質を併記する。

### 手順3：所定の形式で表示する

重要データには、通貨、単位、対象期間、会計基準、基準日を付け、次の形式で示す。

```text
売上高：1,239億元（CNY、FY2025） ✅
  - macrotrends：1,241億元（CNY）
  - stockanalysis：1,237億元（CNY）
  - 差異率：0.3%
```

差異がある場合の例：

```text
純利益：245億元（CNY、FY2025） ⚠️ データに差異あり
  - macrotrends：245億元（CNY、GAAP）
  - stockanalysis：278億元（CNY、Non-GAAP）
  - 差異率：13.5%
  - 想定原因：会計上の定義が異なる（GAAPとNon-GAAP）
```

---

## よくある差異の原因

差異があっても、必ずしもデータ自体が誤っているとは限らない。

| 原因 | 説明 |
|---|---|
| GAAPとNon-GAAP | 特に利益指標で頻繁に生じる |
| 為替換算 | HKD、CNY、USDの換算レートや換算時点が異なる |
| 会計年度の定義 | 暦年と企業独自の会計年度が異なる。例：Appleの会計年度は9月末前後に終了する |
| 連結範囲 | 非支配持分や持分法適用会社の扱いが異なる |
| データ更新の遅れ | 一方のサービスが最新の決算をまだ反映していない |
| 株式分割・ADR比率 | 分割調整やADRと原株の換算比率が異なる |
| 継続事業と全社 | 非継続事業を含むかどうかが異なる |

---

## 特則

1. **未上場企業**（miHoYo、Lilith Gamesなど）：一次情報が1つしかない場合は、データの前に`[推定]`または`[単一情報源]`と記載し、クロスチェック済みと扱わない。
2. **四半期データと年度データ**：クロスチェックでは年度データを優先する。四半期データは情報源によって更新が遅れる場合がある。
3. **一次資料を優先**：2つの二次情報源が10-K、年次報告書などの一次資料と一致しない場合は、一次資料を正本とし、二次情報源の相違を明記する。
4. **通貨と単位**：`亿元`を「億円」と解釈してはならない。人民元なら「億元（CNY）」、香港ドルなら「億HKD」など、通貨を明示する。
5. **期間と会計基準**：年度実績、四半期実績、TTM、会社予想、市場予想を混同しない。GAAP、IFRS、Non-GAAPも明示する。

---

## クイックリファレンス

| 対象 | 主な情報源 | 代替情報源 |
|---|---|---|
| PDD / Pinduoduo | macrotrends.net/stocks/charts/PDD | stockanalysis.com/stocks/pdd |
| Tencent | macrotrends.net/stocks/charts/TCEHY | aastocks（0700.HK） |
| NetEase | macrotrends.net/stocks/charts/NTES | aastocks（9999.HK） |
| 37 Interactive Entertainment | eastmoney.com（002555） | cninfo.com.cn |
| G-bits | eastmoney.com（603444） | cninfo.com.cn |
| Nintendo | macrotrends.net/stocks/charts/NTDOY | stockanalysis.com/stocks/ntdoy |
| Capcom | macrotrends（CCOEY） | stockanalysis（CCOEY） |
