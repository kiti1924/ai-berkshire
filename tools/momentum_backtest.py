#!/usr/bin/env python3
"""モメンタム検出とファンダメンタルズ確認のバックテストツール。

対象：NVDA / AMD / MU
期間：2022年1月から2025年12月
検証内容：AI需要拡大の初期段階で各銘柄を検出できたか。
"""

import json
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from collections import OrderedDict

# ============================================================
# 第1部：過去株価データの取得（Yahoo Finance Chart API）
# ============================================================

def fetch_price_data(ticker, start_date="2021-06-01", end_date="2025-12-31"):
    """Yahoo Finance APIから日次株価データを取得する。"""
    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={start_ts}&period2={end_ts}&interval=1d"
    )
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        rows = []
        for i, ts in enumerate(timestamps):
            dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            c = quote["close"][i]
            v = quote["volume"][i]
            o = quote["open"][i]
            h = quote["high"][i]
            l = quote["low"][i]
            if c and v:
                rows.append({"date": dt, "open": o, "high": h, "low": l, "close": c, "volume": v})
        return rows
    except Exception as e:
        print(f"  [警告] {ticker}の株価データを取得できない: {e}")
        return None


# ============================================================
# 第2部：主要四半期のファンダメンタルズを手入力する。
# 四半期財務APIの安定性が低いため、検証済みの主要数値を固定データとして扱う。
# ============================================================

FUNDAMENTALS = {
    "NVDA": {
        "name": "NVIDIA（エヌビディア）",
        "quarters": OrderedDict([
            # (決算発表日, {売上高（億USD）, 売上高前年同期比, 粗利益率, EPS, EPS上振れ率})
            # FY2023は暦年2022年に相当する。
            ("2022-05-25", {"rev": 82.9, "rev_yoy": 46.0, "gm": 65.5, "eps": 1.36, "eps_beat": 4.6, "label": "FY23Q1 (Apr22)"}),
            ("2022-08-24", {"rev": 67.0, "rev_yoy": -4.0, "gm": 43.5, "eps": 0.51, "eps_beat": -24.0, "label": "FY23Q2 (Jul22)"}),
            ("2022-11-16", {"rev": 59.3, "rev_yoy": -17.0, "gm": 53.6, "eps": 0.58, "eps_beat": 7.4, "label": "FY23Q3 (Oct22)"}),
            ("2023-02-22", {"rev": 60.5, "rev_yoy": -21.0, "gm": 63.3, "eps": 0.88, "eps_beat": 10.0, "label": "FY23Q4 (Jan23)"}),
            # FY2024は暦年2023年に相当し、AI需要が急拡大した。
            ("2023-05-24", {"rev": 71.9, "rev_yoy": -13.0, "gm": 64.6, "eps": 1.09, "eps_beat": 18.5, "label": "FY24Q1 (Apr23) ★ AI需要の転換点"}),
            ("2023-08-23", {"rev": 135.1, "rev_yoy": 101.0, "gm": 70.1, "eps": 2.70, "eps_beat": 29.0, "label": "FY24Q2 (Jul23) ★★ 急拡大"}),
            ("2023-11-21", {"rev": 181.2, "rev_yoy": 206.0, "gm": 74.0, "eps": 4.02, "eps_beat": 19.0, "label": "FY24Q3 (Oct23) ★★★"}),
            ("2024-02-21", {"rev": 221.0, "rev_yoy": 265.0, "gm": 76.0, "eps": 5.16, "eps_beat": 12.0, "label": "FY24Q4 (Jan24)"}),
            ("2024-05-22", {"rev": 260.4, "rev_yoy": 262.0, "gm": 78.4, "eps": 6.12, "eps_beat": 9.0, "label": "FY25Q1 (Apr24)"}),
            ("2024-08-28", {"rev": 300.4, "rev_yoy": 122.0, "gm": 75.1, "eps": 0.68, "eps_beat": 5.6, "label": "FY25Q2 (Jul24)"}),
        ]),
    },
    "AMD": {
        "name": "AMD",
        "quarters": OrderedDict([
            ("2022-05-03", {"rev": 58.9, "rev_yoy": 71.0, "gm": 48.0, "eps": 1.13, "eps_beat": 9.7, "label": "Q1 2022"}),
            ("2022-08-02", {"rev": 65.5, "rev_yoy": 70.0, "gm": 46.0, "eps": 1.05, "eps_beat": 5.0, "label": "Q2 2022"}),
            ("2022-11-01", {"rev": 55.7, "rev_yoy": 29.0, "gm": 42.0, "eps": 0.67, "eps_beat": 2.3, "label": "Q3 2022"}),
            ("2023-01-31", {"rev": 55.0, "rev_yoy": 16.0, "gm": 43.0, "eps": 0.69, "eps_beat": 6.2, "label": "Q4 2022"}),
            ("2023-05-02", {"rev": 53.5, "rev_yoy": -9.0, "gm": 44.0, "eps": 0.60, "eps_beat": 7.1, "label": "Q1 2023"}),
            ("2023-08-01", {"rev": 54.0, "rev_yoy": -18.0, "gm": 46.0, "eps": 0.58, "eps_beat": 1.8, "label": "Q2 2023"}),
            ("2023-10-31", {"rev": 58.0, "rev_yoy": 4.0, "gm": 47.0, "eps": 0.70, "eps_beat": 6.1, "label": "Q3 2023"}),
            ("2024-01-30", {"rev": 61.7, "rev_yoy": 10.0, "gm": 47.0, "eps": 0.77, "eps_beat": 3.7, "label": "Q4 2023 ★ MI300発表"}),
            ("2024-04-30", {"rev": 54.7, "rev_yoy": 2.0, "gm": 47.0, "eps": 0.62, "eps_beat": 3.3, "label": "Q1 2024"}),
            ("2024-07-30", {"rev": 58.3, "rev_yoy": 9.0, "gm": 49.0, "eps": 0.69, "eps_beat": 1.5, "label": "Q2 2024"}),
            ("2024-10-29", {"rev": 68.2, "rev_yoy": 18.0, "gm": 50.0, "eps": 0.92, "eps_beat": 4.5, "label": "Q3 2024 ★ AI需要加速"}),
        ]),
    },
    "MU": {
        "name": "Micron Technology（マイクロン）",
        "quarters": OrderedDict([
            ("2022-06-30", {"rev": 86.4, "rev_yoy": 16.0, "gm": 47.0, "eps": 2.59, "eps_beat": 4.0, "label": "FY22Q3 (May22)"}),
            ("2022-09-29", {"rev": 66.4, "rev_yoy": -20.0, "gm": 40.0, "eps": 1.45, "eps_beat": -5.0, "label": "FY22Q4 (Aug22)"}),
            ("2022-12-21", {"rev": 40.9, "rev_yoy": -47.0, "gm": 22.0, "eps": -0.04, "eps_beat": 22.0, "label": "FY23Q1 (Nov22)"}),
            ("2023-03-28", {"rev": 36.9, "rev_yoy": -53.0, "gm": 11.0, "eps": -1.91, "eps_beat": 5.0, "label": "FY23Q2 (Feb23)"}),
            ("2023-06-28", {"rev": 37.5, "rev_yoy": -57.0, "gm": -8.0, "eps": -1.43, "eps_beat": 15.0, "label": "FY23Q3 (May23)"}),
            ("2023-09-27", {"rev": 40.1, "rev_yoy": -40.0, "gm": -1.0, "eps": -1.07, "eps_beat": 18.0, "label": "FY23Q4 (Aug23) ★ HBM需要の転換点"}),
            ("2023-12-20", {"rev": 47.3, "rev_yoy": 16.0, "gm": 20.0, "eps": -0.95, "eps_beat": 68.0, "label": "FY24Q1 (Nov23) ★★ 業績反転"}),
            ("2024-03-20", {"rev": 58.2, "rev_yoy": 58.0, "gm": 28.0, "eps": 0.42, "eps_beat": 82.0, "label": "FY24Q2 (Feb24) ★★★"}),
            ("2024-06-26", {"rev": 68.1, "rev_yoy": 82.0, "gm": 35.4, "eps": 0.62, "eps_beat": 6.9, "label": "FY24Q3 (May24)"}),
            ("2024-09-25", {"rev": 77.5, "rev_yoy": 93.0, "gm": 36.5, "eps": 1.18, "eps_beat": 5.4, "label": "FY24Q4 (Aug24)"}),
        ]),
    },
}


# ============================================================
# 第3部：モメンタム検出（第1段階）
# ============================================================

def compute_momentum_signals(prices):
    """モメンタムシグナルを計算する。"""
    signals = []
    for i in range(60, len(prices)):
        row = prices[i]
        date = row["date"]
        close = row["close"]

        # 60日高値更新
        past_60_highs = [prices[j]["high"] for j in range(i - 60, i)]
        is_60d_high = close > max(past_60_highs)

        # 出来高確認：直近5日平均 > 20日平均の1.8倍
        vol_5 = sum(prices[j]["volume"] for j in range(i - 4, i + 1)) / 5
        vol_20 = sum(prices[j]["volume"] for j in range(i - 19, i + 1)) / 20
        is_volume_surge = vol_5 > vol_20 * 1.8

        # 30日騰落率
        close_30d_ago = prices[i - 30]["close"]
        pct_30d = (close - close_30d_ago) / close_30d_ago * 100

        # 総合判定
        momentum_triggered = is_60d_high and is_volume_surge

        if momentum_triggered:
            signals.append({
                "date": date,
                "close": round(close, 2),
                "pct_30d": round(pct_30d, 1),
                "vol_ratio": round(vol_5 / vol_20, 2),
                "is_60d_high": is_60d_high,
            })

    return signals


# ============================================================
# 第4部：ファンダメンタルズ確認（第2段階）
# ============================================================

def find_latest_fundamental(ticker, signal_date):
    """シグナル日以前で最新の四半期決算を取得する。"""
    quarters = FUNDAMENTALS[ticker]["quarters"]
    latest = None
    latest_date = None
    for q_date, q_data in quarters.items():
        if q_date <= signal_date:
            latest = q_data
            latest_date = q_date
    return latest_date, latest


def verify_value(ticker, fund_data, prev_fund_data=None):
    """5項目でファンダメンタルズを確認する。"""
    if not fund_data:
        return {"score": 0, "details": "ファンダメンタルズデータなし"}

    checks = {}

    # 1. 売上高成長率が改善している。
    rev_yoy = fund_data.get("rev_yoy", 0)
    if prev_fund_data:
        prev_rev_yoy = prev_fund_data.get("rev_yoy", 0)
        rev_accelerating = rev_yoy > prev_rev_yoy
    else:
        rev_accelerating = rev_yoy > 20
    checks["売上高成長の加速"] = rev_accelerating

    # 2. 粗利益率が45%を超え、悪化していない。
    gm = fund_data.get("gm", 0)
    if prev_fund_data:
        prev_gm = prev_fund_data.get("gm", 0)
        gm_expanding = gm > prev_gm or gm > 50
    else:
        gm_expanding = gm > 45
    checks["粗利益率の改善"] = gm_expanding

    # 3. EPSが市場予想を10%超上回る。
    eps_beat = fund_data.get("eps_beat", 0)
    checks["EPSの上振れ"] = eps_beat > 10

    # 4. 売上高成長率が15%を超える。
    checks["高い売上高成長"] = rev_yoy > 15

    # 5. 粗利益率が40%を超える。
    checks["健全な粗利益率"] = gm > 40

    score = sum(1 for v in checks.values() if v)
    return {"score": score, "max": 5, "details": checks, "fund": fund_data}


# ============================================================
# 第5部：バックテスト本体
# ============================================================

def backtest_ticker(ticker):
    """1銘柄についてバックテストを実行する。"""
    print(f"\n{'='*70}")
    print(f"  バックテスト対象：{FUNDAMENTALS[ticker]['name']} ({ticker})")
    print(f"{'='*70}")

    # 株価データを取得する。
    print("\n  [1/3] 過去株価データを取得中...")
    prices = fetch_price_data(ticker, "2021-06-01", "2025-06-30")
    if not prices:
        print("  ❌ 株価データを取得できないため、対象外とする")
        return None

    print(f"  {len(prices)}取引日を取得した ({prices[0]['date']} ～ {prices[-1]['date']})")

    # モメンタムシグナルを計算する。
    print("\n  [2/3] モメンタムシグナルを走査中...")
    momentum_signals = compute_momentum_signals(prices)
    print(f"  {len(momentum_signals)}件のモメンタム発生点を検出した")

    # ファンダメンタルズを確認する。
    print("\n  [3/3] モメンタム発生点のファンダメンタルズを確認中...")

    buy_signals = []
    seen_months = set()

    for sig in momentum_signals:
        month_key = sig["date"][:7]
        if month_key in seen_months:
            continue  # 同じ月は最初のシグナルだけを採用する。
        seen_months.add(month_key)

        # 利用可能なファンダメンタルズを取得する。
        q_date, fund = find_latest_fundamental(ticker, sig["date"])
        if not fund:
            continue

        # 前四半期と比較する。
        quarters_list = list(FUNDAMENTALS[ticker]["quarters"].items())
        prev_fund = None
        for idx, (qd, qf) in enumerate(quarters_list):
            if qd == q_date and idx > 0:
                prev_fund = quarters_list[idx - 1][1]
                break

        verification = verify_value(ticker, fund, prev_fund)

        result = {
            "date": sig["date"],
            "close": sig["close"],
            "pct_30d": sig["pct_30d"],
            "vol_ratio": sig["vol_ratio"],
            "fund_date": q_date,
            "fund_label": fund.get("label", ""),
            "value_score": verification["score"],
            "value_max": verification["max"],
            "details": verification["details"],
            "rev_yoy": fund.get("rev_yoy", "N/A"),
            "gm": fund.get("gm", "N/A"),
            "eps_beat": fund.get("eps_beat", "N/A"),
        }

        # 5項目中3項目以上なら買いシグナルとする。
        if verification["score"] >= 3:
            result["action"] = "✅ 買いシグナル"
            buy_signals.append(result)
        else:
            result["action"] = "❌ 不合格"

    # 結果を表示する。
    print(f"\n  {'—'*60}")
    print("  モメンタム検出 + ファンダメンタルズ確認の結果：")
    print(f"  {'—'*60}")

    all_signals_with_action = []
    for sig in momentum_signals:
        month_key = sig["date"][:7]
        found = False
        for bs in buy_signals:
            if bs["date"][:7] == month_key:
                all_signals_with_action.append(bs)
                found = True
                break

    # 主要な期間のシグナルだけを表示する。
    first_buy = None
    for bs in buy_signals:
        if bs["date"] >= "2022-06-01":
            if not first_buy:
                first_buy = bs
            print(f"\n  📅 {bs['date']} | 終値 ${bs['close']}")
            print(f"     モメンタム：30日騰落率 {bs['pct_30d']}% | 出来高倍率 {bs['vol_ratio']}x")
            print(f"     ファンダメンタルズ（{bs['fund_label']}）：")
            print(f"       売上高前年同期比 {bs['rev_yoy']}% | 粗利益率 {bs['gm']}% | EPS上振れ {bs['eps_beat']}%")
            print(f"     確認結果：{bs['value_score']}/{bs['value_max']} ", end="")
            for k, v in bs["details"].items():
                print(f"{'✅' if v else '❌'}{k} ", end="")
            print(f"\n     判定：{bs['action']}")

    # 仮想リターンを計算する。
    if first_buy and prices:
        buy_price = first_buy["close"]
        buy_date = first_buy["date"]
        # 最終観測日の株価を取得する。
        for p in prices:
            if p["date"] >= buy_date:
                final_price = p["close"]
        final_date = prices[-1]["date"]
        total_return = (final_price - buy_price) / buy_price * 100

        print(f"\n  {'='*60}")
        print("  📊 最初のシグナルを適用した場合：")
        print(f"     基準日：{buy_date} @ ${buy_price}")
        print(f"     最終日：{final_date} @ ${round(final_price, 2)}")
        print(f"     累積リターン：{round(total_return, 1)}%")
        print(f"  {'='*60}")

    return {"ticker": ticker, "buy_signals": buy_signals, "first_buy": first_buy}


# ============================================================
# メイン処理
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  モメンタム検出 + ファンダメンタルズ確認 バックテスト")
    print("  対象：NVDA / AMD / MU | 期間：2022-2025")
    print("=" * 70)

    results = {}
    for ticker in ["NVDA", "AMD", "MU"]:
        result = backtest_ticker(ticker)
        if result:
            results[ticker] = result

    # 集計
    print(f"\n\n{'='*70}")
    print("  📋 バックテスト概要")
    print(f"{'='*70}")
    print(f"\n  {'銘柄':<8} {'最初のシグナル':<16} {'基準価格':<12} {'判定時の決算'}")
    print(f"  {'—'*65}")
    for ticker, r in results.items():
        if r["first_buy"]:
            fb = r["first_buy"]
            print(f"  {ticker:<8} {fb['date']:<16} ${fb['close']:<10} {fb['fund_label']}")
        else:
            print(f"  {ticker:<8} {'シグナルなし':<16}")

    print("\n  検証結果：")
    print(f"  ┌─────────────────────────────────────────────────────────────┐")
    print("  │ AI需要拡大の初期段階でNVDA・AMD・MUを検出できたか。       │")
    print("  │ 結果は上記のシグナルとリターンを参照すること。             │")
    print(f"  └─────────────────────────────────────────────────────────────┘")
