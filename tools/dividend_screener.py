#!/usr/bin/env python3
"""dividend_screener.py — 配当利回りと52週高値からの下落率による銘柄選別。

使用例：
  python3 tools/dividend_screener.py                   # watchlist全体を走査する
  python3 tools/dividend_screener.py NVDA AAPL VZ T   # 指定銘柄を走査する
  python3 tools/dividend_screener.py --min-yield 5.0 --min-drop 20.0 # 閾値を変更して走査する
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

# ============================================================
# 設定
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.json")

DEFAULT_WATCHLIST = {
    "us_ai_chip": ["NVDA", "AMD", "MU", "AVGO", "MRVL", "TSM"],
    "us_ai_app": ["GOOG", "META", "MSFT", "AMZN", "CRM", "NOW", "PLTR"],
    "us_ai_infra": ["ETN", "PWR", "VRT", "CRWV"],
}

# ============================================================
# データ取得（curlを使いSSL問題を回避）
# ============================================================

def fetch_chart_curl(ticker):
    """Yahoo Finance APIのchartエンドポイントから過去1年の株価と配当データを取得する。"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1y&interval=1d&events=div"
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        
        # 必要な情報を抽出
        res = data.get("chart", {}).get("result")
        if not res or len(res) == 0:
            return None
        
        return res[0]
    except Exception:
        return None

# ============================================================
# 判定処理
# ============================================================

def check_stock(ticker, chart_data, min_yield=4.0, min_drop=15.0):
    """取得したデータから配当利回りと下落率をチェックする。"""
    if not chart_data:
        return None
        
    meta = chart_data.get("meta", {})
    price = meta.get("regularMarketPrice")
    
    # regularMarketPriceが取れない場合は最後の日の終値をフォールバックにする
    if not price:
        quote = chart_data.get("indicators", {}).get("quote", [{}])[0]
        closes = [c for c in quote.get("close", []) if c is not None]
        if closes:
            price = closes[-1]
            
    if not price or price <= 0:
        return None
        
    # 52週高値の計算（過去1年の高値の最大値）
    quote = chart_data.get("indicators", {}).get("quote", [{}])[0]
    highs = [h for h in quote.get("high", []) if h is not None]
    high_52w = max(highs) if highs else price
    
    if high_52w <= 0:
        return None

    # 過去1年の配当金の合算
    dividends = chart_data.get("events", {}).get("dividends", {})
    div_rate = 0.0
    for timestamp, div_info in dividends.items():
        amount = div_info.get("amount", 0.0)
        div_rate += amount

    # 配当利回りの計算
    div_yield = (div_rate / price * 100.0)

    # 下落率の計算
    drop_pct = (high_52w - price) / high_52w * 100.0

    # 判定基準
    is_yield_ok = div_yield >= min_yield
    is_drop_ok = drop_pct >= min_drop
    triggered = is_yield_ok and is_drop_ok

    currency = meta.get("currency", "USD")

    return {
        "ticker": ticker,
        "price": price,
        "high_52w": high_52w,
        "div_yield": round(div_yield, 2),
        "div_rate": round(div_rate, 3),
        "drop_pct": round(drop_pct, 2),
        "currency": currency,
        "triggered": triggered,
        "is_yield_ok": is_yield_ok,
        "is_drop_ok": is_drop_ok
    }

# ============================================================
# メイン処理
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="高配当・下落株スクリーナー")
    parser.add_argument("tickers", nargs="*", help="個別に走査する銘柄コード")
    parser.add_argument("--min-yield", type=float, default=4.0, help="最小配当利回り（%%）のしきい値。デフォルト: 4.0%%")
    parser.add_argument("--min-drop", type=float, default=15.0, help="52週高値からの最小下落率（%%）のしきい値。デフォルト: 15.0%%")
    
    args = parser.parse_args()

    # 走査対象の決定
    if args.tickers:
        tickers = [t.upper() for t in args.tickers]
    else:
        # ウォッチリストファイルの読み込み
        if os.path.exists(WATCHLIST_FILE):
            try:
                with open(WATCHLIST_FILE, encoding="utf-8") as f:
                    wl = json.load(f)
                tickers = []
                for group, syms in wl.items():
                    tickers.extend(syms)
            except Exception as e:
                print(f"  ⚠️  Watchlistの読み込みに失敗しました: {e}")
                sys.exit(1)
        else:
            # 既定のリスト
            tickers = []
            for group, syms in DEFAULT_WATCHLIST.items():
                tickers.extend(syms)

    # 重複を削除してソート
    tickers = sorted(list(set(tickers)))

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*75}")
    print(f"  高配当かつ価格下落株スクリーニング  {today}")
    print(f"  条件: 配当利回り ≧ {args.min_yield:.2f}% かつ 52週高値からの下落率 ≧ {args.min_drop:.2f}%")
    print(f"  走査対象：{len(tickers)}銘柄")
    print(f"{'='*75}\n")

    hits = []

    for i, ticker in enumerate(tickers):
        # 連続アクセスの場合は少しウェイトを入れる
        if i > 0:
            time.sleep(0.5)

        chart_data = fetch_chart_curl(ticker)
        if not chart_data:
            # 日本株などのために .T を付与して再試行
            if "." not in ticker:
                chart_data = fetch_chart_curl(f"{ticker}.T")
                if chart_data:
                    ticker = f"{ticker}.T"
            
        if not chart_data:
            print(f"  ⚠️  {ticker:<8} データを取得できません")
            continue

        result = check_stock(ticker, chart_data, args.min_yield, args.min_drop)
        if not result:
            print(f"  ⬜  {ticker:<8} 必要データ（株価・配当）が不足しています")
            continue

        if result["triggered"]:
            hits.append(result)
            symbol = "🎯"
        else:
            symbol = "⬜"

        # 1行で進捗表示
        curr_symbol = "$" if result["currency"] == "USD" else result["currency"] + " "
        print(f"  {symbol} {result['ticker']:<8} 価格: {curr_symbol}{result['price']:>7.2f}  "
              f"配当利回り: {result['div_yield']:>5.2f}% (年 {curr_symbol}{result['div_rate']:.3f})  "
              f"52週高値下落率: {result['drop_pct']:>5.2f}%")

    # 集計結果の表示
    print(f"\n{'='*75}")
    print(f"  📋 スクリーニング結果集計 (ヒット数: {len(hits)} / 走査数: {len(tickers)})")
    print(f"{'='*75}")

    if hits:
        # 配当利回りが高い順に並べる
        hits.sort(key=lambda x: x["div_yield"], reverse=True)
        print(f"\n  🎯 基準を満たした銘柄（配当利回り順）:")
        print(f"  {'Ticker':<10} {'現在値':>10} {'配当利回り':>12} {'年配当額':>10} {'52週高値':>10} {'下落率':>10}")
        print(f"  {'-'*70}")
        for h in hits:
            curr_symbol = "$" if h["currency"] == "USD" else h["currency"] + " "
            print(f"  {h['ticker']:<10} "
                  f"{curr_symbol}{h['price']:>8.2f} "
                  f"{h['div_yield']:>11.2f}% "
                  f"{curr_symbol}{h['div_rate']:>8.2f} "
                  f"{curr_symbol}{h['high_52w']:>8.2f} "
                  f"{h['drop_pct']:>9.2f}%")
    else:
        print("\n  基準を満たす銘柄は見つかりませんでした。")

    print()

if __name__ == "__main__":
    main()
