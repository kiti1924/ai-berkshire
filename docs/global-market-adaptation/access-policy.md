# Global Market Adaptation Access Policy Specification

- 文書ID: `ABG-ACCESS-POLICY-SPEC`
- 上位仕様: `docs/global-market-adaptation/spec.md` (`ABG-MARKET-ADAPTATION-SPEC`)
- 状態: Draft

## 1. 概要

本仕様書は、外部Webサイトおよび公開API（SEC EDGAR, EDINET, TDnet, SSE, HKEXnews等）へのオンデマンドアクセス制御、レート制限、キャッシュ利用、および失敗時の安全な劣化動作を定義する。

## 2. アクセス制御パラメータ (Default Settings)

```yaml
web_access:
  cache_first: true
  max_concurrent_requests_per_domain: 1
  minimum_interval_seconds: 3.0
  exponential_backoff: true
  respect_retry_after: true
  stop_on_403: true
  stop_on_repeated_429: true
  bulk_crawling: false
```

## 3. レスポンスステータス処理

1. **429 Too Many Requests**: `Retry-After` ヘッダーを尊重し待機。ヘッダーが無い場合は指数バックオフを行う。連続429発生時は即時アクセスを中断しキャッシュまたは二次情報へ切替。
2. **403 Forbidden**: 即時アクセスを停止し、代替公式情報源またはIR資料へ移行。迂回行為（代理プロキシや偽装等）は禁止。
3. **503 Service Unavailable**: バックオフ後に再試行。失敗時は情報不足を明示して `partial` レポートを出力。

## 4. 禁止事項

- CAPTCHA自動回避・突破
- ログインセッションの流用・迂回
- 同一ドメインへの短時間大量並列アクセス
- 全市場・全上場企業の巡回収集 (Bulk crawling / Scraping)
