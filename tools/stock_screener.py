#!/usr/bin/env python3
"""stock_screener.py — モメンタム検出とファンダメンタルズ確認による銘柄選別。

使用例：
  python3 stock_screener.py                   # watchlist全体を走査する
  python3 stock_screener.py NVDA TSLA GOOG    # 指定銘柄を走査する
  python3 stock_screener.py --update MU       # MUのファンダメンタルズを更新する

判定手順：
  第1段階（モメンタム検出）：60日高値更新 + 出来高増加 → 候補へ追加
  第2段階（価値確認）：6項目中3項目以上 → 買いシグナル
  シグナル区分：3/6=試行3% | 4/6=標準5% | 5-6/6=高確信8%

NVDA・AMD・MUのバックテストを踏まえた補助条件：
  1. 粗利益率が2四半期連続で改善する場合は独立条件とする
  2. EPSが市場予想を30%超上回る場合は循環株の独立条件とする
  3. 二値判定ではなく段階別シグナルを使用する
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from collections import OrderedDict

# ============================================================
# 設定
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
FUND_FILE = os.path.join(DATA_DIR, "fundamentals.json")
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.json")

DEFAULT_WATCHLIST = {
    "us_ai_chip": ["NVDA", "AMD", "MU", "AVGO", "MRVL", "TSM"],
    "us_ai_app": ["GOOG", "META", "MSFT", "AMZN", "CRM", "NOW", "PLTR"],
    "us_ai_infra": ["ETN", "PWR", "VRT", "CRWV"],
    "us_crypto": ["COIN", "HOOD", "MSTR", "CRCL"],
    "hk_internet": ["0700.HK", "9888.HK", "1024.HK", "9992.HK"],
    "a_share": [],  # 中国本土A株は別のデータ源が必要であり、将来拡張する。
}

# ============================================================
# 株価データ取得（curlを使いPython側のSSL問題を回避する）
# ============================================================

def fetch_prices_curl(ticker, days=120):
    """curlでYahoo Financeの日次データを取得する。"""
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(days=days)).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={start_ts}&period2={end_ts}&interval=1d"
    )
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        chart = data.get("chart", {}).get("result", [{}])[0]
        timestamps = chart.get("timestamp", [])
        quote = chart.get("indicators", {}).get("quote", [{}])[0]
        rows = []
        for i, ts in enumerate(timestamps):
            c = quote.get("close", [None] * len(timestamps))[i]
            v = quote.get("volume", [None] * len(timestamps))[i]
            h = quote.get("high", [None] * len(timestamps))[i]
            if c and v and h:
                dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                rows.append({"date": dt, "close": c, "high": h, "volume": v})
        return rows if len(rows) > 60 else None
    except Exception as e:
        return None


# ============================================================
# ファンダメンタルズデータ管理
# ============================================================

def load_fundamentals():
    """ファンダメンタルズデータを読み込む。"""
    if os.path.exists(FUND_FILE):
        with open(FUND_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_fundamentals(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FUND_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)



def update_fundamental_interactive(ticker):
    """対話形式でファンダメンタルズデータを更新する。"""
    funds = load_fundamentals()
    if ticker not in funds:
        funds[ticker] = {"quarters": {}}
    print(f"\n  {ticker}のファンダメンタルズを更新する")
    print(f"  登録済み四半期：{', '.join(funds[ticker]['quarters'].keys()) or 'なし'}")
    date = input("  決算発表日 (YYYY-MM-DD): ").strip()
    label = input("  ラベル（例: Q1 2024）: ").strip()
    rev_yoy = float(input("  売上高前年同期比 (%): "))
    gm = float(input("  粗利益率 (%): "))
    eps_beat = float(input("  EPSの市場予想超過率 (%): "))

    funds[ticker]["quarters"][date] = {
        "label": label, "rev_yoy": rev_yoy, "gm": gm, "eps_beat": eps_beat
    }
    save_fundamentals(funds)
    print(f"  ✅ {ticker} {label}を保存した")


# ============================================================
# 第1段階：モメンタム検出
# ============================================================

def check_momentum(prices):
    """直近取引日にモメンタムシグナルが発生したかを確認する。"""
    if len(prices) < 61:
        return None

    latest = prices[-1]
    close = latest["close"]

    # 60日高値更新
    past_60_highs = [p["high"] for p in prices[-61:-1]]
    is_60d_high = close > max(past_60_highs)

    # 出来高増加：直近5日平均 > 20日平均 × 1.5
    vol_5 = sum(p["volume"] for p in prices[-5:]) / 5
    vol_20 = sum(p["volume"] for p in prices[-20:]) / 20
    vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 0
    is_volume = vol_ratio > 1.5

    # 30日騰落率
    close_30d = prices[-31]["close"] if len(prices) > 30 else prices[0]["close"]
    pct_30d = (close - close_30d) / close_30d * 100

    # 直近5日以内の高値更新も対象にする。
    recent_breakout = False
    for i in range(-5, 0):
        if prices[i]["close"] > max(p["high"] for p in prices[i-60:i]):
            recent_breakout = True
            break

    triggered = (is_60d_high or recent_breakout) and is_volume

    return {
        "triggered": triggered,
        "close": round(close, 2),
        "date": latest["date"],
        "is_60d_high": is_60d_high,
        "vol_ratio": round(vol_ratio, 2),
        "pct_30d": round(pct_30d, 1),
    }


# ============================================================
# 第2段階：ファンダメンタルズ確認（6項目、補助条件を含む）
# ============================================================

def check_value(ticker, signal_date=None):
    """6項目でファンダメンタルズを確認する。"""
    funds = load_fundamentals()
    if ticker not in funds or not funds[ticker].get("quarters"):
        return None

    quarters = funds[ticker]["quarters"]
    sorted_q = sorted(quarters.items(), key=lambda x: x[0])

    # 指定日時点で利用可能な直近四半期を選ぶ。
    if signal_date:
        valid = [(d, q) for d, q in sorted_q if d <= signal_date]
    else:
        valid = sorted_q

    if not valid:
        return None

    latest = valid[-1]
    prev = valid[-2] if len(valid) >= 2 else None
    prev2 = valid[-3] if len(valid) >= 3 else None

    d = latest[1]
    pd = prev[1] if prev else None
    pd2 = prev2[1] if prev2 else None

    checks = {}

    # 1. 売上高成長率が改善している。
    if pd:
        checks["売上高成長の加速"] = d["rev_yoy"] > pd["rev_yoy"]
    else:
        checks["売上高成長の加速"] = d["rev_yoy"] > 20

    # 2. 粗利益率が改善している。
    if pd:
        checks["粗利益率の改善"] = d["gm"] > pd["gm"] or d["gm"] > 55
    else:
        checks["粗利益率の改善"] = d["gm"] > 45

    # 3. EPSが市場予想を10%超上回る。
    checks["EPSの上振れ"] = d["eps_beat"] > 10

    # 4. 売上高成長率が15%を超える。
    checks["高い売上高成長"] = d["rev_yoy"] > 15

    # 5. 粗利益率が40%を超える。
    checks["健全な粗利益率"] = d["gm"] > 40

    # 6. 粗利益率が2四半期連続で改善する。
    if pd and pd2:
        checks["粗利益率の連続改善"] = d["gm"] > pd["gm"] > pd2["gm"]
    elif pd:
        checks["粗利益率の連続改善"] = d["gm"] > pd["gm"]
    else:
        checks["粗利益率の連続改善"] = False

    score = sum(1 for v in checks.values() if v)

    # 独立した合格条件
    independent_pass = False
    independent_reason = ""

    if checks.get("粗利益率の連続改善") and d["gm"] > 45:
        independent_pass = True
        independent_reason = "粗利益率が連続改善し45%超"

    if d["eps_beat"] > 30:
        independent_pass = True
        independent_reason = "EPSが市場予想を30%超上回る（循環株シグナル）"

    return {
        "score": score,
        "max": 6,
        "checks": checks,
        "fund": d,
        "fund_date": latest[0],
        "fund_label": d.get("label", ""),
        "independent_pass": independent_pass,
        "independent_reason": independent_reason,
    }


# ============================================================
# シグナル区分
# ============================================================

def grade_signal(momentum, value):
    """モメンタムとファンダメンタルズを総合評価する。"""
    if not momentum or not momentum["triggered"]:
        return "SKIP", "モメンタムシグナルなし", ""

    if not value:
        return "WATCH", "モメンタム発生、ファンダメンタルズ未登録", "ファンダメンタルズを補完"

    score = value["score"]
    ind = value["independent_pass"]

    if score >= 5 or (score >= 4 and ind):
        return "BUY_8%", f"高確信（{score}/6）", "8%配分の検討"
    elif score >= 4 or (score >= 3 and ind):
        return "BUY_5%", f"標準（{score}/6）", "5%配分の検討"
    elif score >= 3:
        return "BUY_3%", f"試行（{score}/6）", "3%配分の検討"
    elif ind:
        return "BUY_3%", f"独立条件に合格：{value['independent_reason']}", "3%配分の検討"
    else:
        return "PASS", f"モメンタムはあるが確認項目不足（{score}/6）", "継続観察"


# ============================================================
# 1銘柄の走査
# ============================================================

def scan_ticker(ticker, verbose=True):
    """1銘柄を走査する。"""
    prices = fetch_prices_curl(ticker)
    if not prices:
        if verbose:
            print(f"  {ticker:<8} ⚠️  株価データを取得できない")
        return None

    momentum = check_momentum(prices)
    value = check_value(ticker)
    grade, reason, advice = grade_signal(momentum, value)

    result = {
        "ticker": ticker,
        "grade": grade,
        "reason": reason,
        "advice": advice,
        "momentum": momentum,
        "value": value,
    }

    if verbose:
        # 簡潔な形式で表示する。
        m = momentum
        symbol = {"BUY_8%": "🔴", "BUY_5%": "🟡", "BUY_3%": "🟢", "WATCH": "👀", "PASS": "⬜", "SKIP": "  "}
        s = symbol.get(grade, "  ")

        if grade.startswith("BUY"):
            print(f"  {s} {ticker:<8} ${m['close']:<8} 30日{m['pct_30d']:+}% 出来高倍率{m['vol_ratio']}x  → {grade} {reason}")
            if value:
                v = value
                checks_str = " ".join(f"{'✅' if val else '❌'}{k}" for k, val in v["checks"].items())
                print(f"     ファンダメンタルズ（{v['fund_label']}）: 売上高前年同期比{v['fund']['rev_yoy']}% 粗利益率{v['fund']['gm']}% EPS上振れ{v['fund']['eps_beat']}%")
                print(f"     {checks_str}")
                if v["independent_pass"]:
                    print(f"     ★独立条件に合格：{v['independent_reason']}")
        elif grade == "WATCH":
            print(f"  {s} {ticker:<8} ${m['close']:<8} 30日{m['pct_30d']:+}%  → モメンタム発生。ファンダメンタルズの補完が必要")
        elif grade == "PASS":
            print(f"  {s} {ticker:<8} ${m['close']:<8}  → {reason}")
        # SKIPは表示しない。

    return result


# ============================================================
# メイン処理
# ============================================================

def main():
    args = sys.argv[1:]

    # 更新モード
    if args and args[0] == "--update":
        ticker = args[1] if len(args) > 1 else input("  銘柄コード: ").strip().upper()
        update_fundamental_interactive(ticker)
        return

    # 既定のwatchlistを初期化する。
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_WATCHLIST, f, indent=2, ensure_ascii=False)
        print(f"  既定のwatchlistを作成した: {WATCHLIST_FILE}")

    # 走査対象を決定する。
    if args:
        tickers = [t.upper() for t in args]
    else:
        with open(WATCHLIST_FILE, encoding="utf-8") as f:
            wl = json.load(f)

        tickers = []
        for group, syms in wl.items():
            tickers.extend(syms)

    # 走査を実行する。
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*70}")
    print(f"  モメンタム検出 + ファンダメンタルズ確認  {today}")
    print(f"  走査対象：{len(tickers)}銘柄")
    print(f"{'='*70}\n")

    buy_signals = []
    watch_signals = []

    for ticker in tickers:
        result = scan_ticker(ticker)
        if result:
            if result["grade"].startswith("BUY"):
                buy_signals.append(result)
            elif result["grade"] == "WATCH":
                watch_signals.append(result)

    # 集計
    print(f"\n{'='*70}")
    print("  📋 走査結果")
    print(f"{'='*70}")

    if buy_signals:
        print(f"\n  🎯 買いシグナル：{len(buy_signals)}件")
        for s in sorted(buy_signals, key=lambda x: x["grade"], reverse=True):
            m = s["momentum"]
            print(f"     {s['grade']:<8} {s['ticker']:<8} ${m['close']:<8} {s['reason']}")
    else:
        print("\n  買いシグナルなし")

    if watch_signals:
        print(f"\n  👀 要観察（ファンダメンタルズ要補完）：{len(watch_signals)}件")
        for s in watch_signals:
            m = s["momentum"]
            print(f"     {s['ticker']:<8} ${m['close']:<8} 30日{m['pct_30d']:+}% — --update {s['ticker']}で補完すること")

    print(f"\n  ファンダメンタルズファイル：{FUND_FILE}")
    print(f"  Watchlistファイル：{WATCHLIST_FILE}")
    print("  --update TICKERでファンダメンタルズを追加・更新できる\n")


if __name__ == "__main__":
    main()
