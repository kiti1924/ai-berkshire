# Global Market Adaptation Data Contract Specification

- 文書ID: `ABG-DATA-CONTRACT-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、米国（US）、日本（JP）、上海A株（CN_SH_A）、香港（HK）の4市場における投資研究共通データ構造（Security, Document, Fact, Evidence, Research Run）の最小契約および正規化ルールを定義する。

## 2. Canonical Data Models

### 2.1 Security Model

```yaml
security:
  security_id: string          # Canonical security identifier (e.g. US:AAPL, JP:7203, CN_SH_A:600519, HK:0700)
  issuer_id: string            # Issuer identifier (e.g. US:CIK0000320193, JP:EDINET_E02144)
  market_id: US | JP | CN_SH_A | HK
  ticker: string               # Exchange ticker or security code
  exchange: string             # Exchange name (NASDAQ, NYSE, TSE, SSE, HKEX)
  legal_name: string           # Official legal entity name
  display_name: string         # Short readable name
  security_type: string        # equity, adr, h_share, red_chip, etc.
  trading_currency: string     # USD, JPY, CNY, HKD
  reporting_currency: string   # USD, JPY, CNY, HKD
  primary_listing: boolean
  identifiers:
    cik: string | null
    edinet_code: string | null
    isin: string | null
    exchange_code: string | null
```

### 2.2 Document Model

```yaml
document:
  document_id: string          # Unique hash or ID for document
  security_id: string
  document_type: string        # 10-K, 10-Q, yuka_shoken_hokokusho, annual_report, etc.
  title: string
  published_at: datetime | null # ISO 8601 UTC with timezone offset
  retrieved_at: datetime      # ISO 8601 UTC with timezone offset
  source_name: string          # SEC_EDGAR, EDINET, TDnet, SSE, HKEXnews, IR_SITE
  source_type: official | secondary | web
  source_url: string
  local_cache_path: string | null
  content_hash: string | null  # SHA256 of downloaded file content
  language: string             # en, ja, zh-cn, zh-hk
  is_official: boolean
  supersedes_document_id: string | null
```

### 2.3 Fact Model

```yaml
fact:
  fact_id: string
  security_id: string
  metric: string               # canonical metric name (revenue, net_income, market_cap, etc.)
  value: number | string | boolean
  unit: string | null          # shares, ratio, currency_amount
  currency: string | null      # USD, JPY, CNY, HKD
  period_start: date | null    # YYYY-MM-DD
  period_end: date | null      # YYYY-MM-DD
  as_of: datetime | null       # timestamp for point-in-time metrics
  retrieved_at: datetime
  source_document_id: string | null
  source_url: string
  source_rank: integer         # 100=Official, 95=Exchange, 90=IR, 70=Structured 2nd, 60=Portal
  accounting_standard: string | null # US-GAAP, J-GAAP, IFRS, CAS
  consolidation: consolidated | standalone | unknown
  fact_type: reported | forecast | estimate | normalized
  verification_status: unverified | single_source | cross_checked | official
```

### 2.4 Evidence Model

```yaml
evidence:
  evidence_id: string
  claim_id: string
  statement: string            # Extracted statement or exact claim support excerpt
  source_document_id: string | null
  source_url: string
  source_rank: integer
  published_at: datetime | null
  retrieved_at: datetime
  supports_claim: boolean
  confidence: low | medium | high
```

### 2.5 Research Run Model

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
  documents_used: [string]     # list of document_ids
  facts_used: [string]         # list of fact_ids
  warnings: [string]
  status: completed | partial | failed
```

## 3. Validation Rules

1. **Datetimes**: Must be timezone-aware ISO 8601 strings (e.g., `2026-06-29T10:00:00Z` or `+09:00`). Naive datetimes are strictly rejected.
2. **Currencies and Units**: Must never be null when `metric` represents financial monetary values.
3. **Verification Status**: Enforced as canonical enum `[unverified, single_source, cross_checked, official]`.
4. **Market ID**: Enforced as canonical enum `[US, JP, CN_SH_A, HK]`.
