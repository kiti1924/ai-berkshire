#!/usr/bin/env python3
"""MorningstarスクリーナーAPIから公正価値推定のある銘柄を取得し、
上昇余地を計算して上位100銘柄を表示する。
"""

import json
import subprocess
import time
import csv
import os
from datetime import datetime

API_BASE = (
    "https://lt.morningstar.com/api/rest.svc/klr5zyak8x/security/screener"
    "?page={page}&pageSize={page_size}"
    "&sortOrder=FairValueEstimate%20desc"
    "&outputType=json&version=1"
    "&languageId=en-US&currencyId=USD"
    "&universeIds=E0EXG%24XNAS%7CE0EXG%24XNYS"
    "&securityDataPoints=SecId%7CName%7CPriceCurrency%7CTenforeId%7CClosePrice"
    "%7CStarRatingM255%7CQuantitativeFairValue%7CFairValueEstimate"
    "%7CAssessmentOfFairValueUncertainty%7CEconomicMoat%7CIndustryName%7CSectorName"
    "&filters=FairValueEstimate:notnull"
)

PAGE_SIZE = 100
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def fetch_page(page: int) -> dict:
    url = API_BASE.format(page=page, page_size=PAGE_SIZE)
    result = subprocess.run(
        ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout)


def extract_ticker(tenforeid: str) -> str:
    if not tenforeid:
        return ""
    parts = tenforeid.split(".")
    return parts[-1] if len(parts) >= 3 else tenforeid


def main():
    print(f"\n{'='*80}")
    print(f"  Morningstar 公正価値スクリーニング  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}\n")

    # 1ページ目から総件数を取得する。
    print("  1ページ目を取得中...")
    data = fetch_page(1)
    total = data.get("total", 0)
    all_rows = data.get("rows", [])
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"  対象は{total}銘柄、全{total_pages}ページである\n")

    # 残りのページを取得する。
    for page in range(2, total_pages + 1):
        if page % 10 == 0 or page == total_pages:
            print(f"  {page}/{total_pages}ページを取得中...")
        try:
            data = fetch_page(page)
            rows = data.get("rows", [])
            if not rows:
                break
            all_rows.extend(rows)
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️  {page}ページ目の取得に失敗した: {e}")
            time.sleep(1)

    print(f"\n  {len(all_rows)}件を取得した")

    # 公正価値までの上昇余地を計算する。
    stocks = []
    for row in all_rows:
        fair_value = row.get("FairValueEstimate")
        close_price = row.get("ClosePrice")
        if not fair_value or not close_price or close_price <= 0:
            continue

        ticker = extract_ticker(row.get("TenforeId", ""))
        upside = (fair_value - close_price) / close_price * 100

        stocks.append({
            "ticker": ticker,
            "name": row.get("Name", ""),
            "close_price": round(close_price, 2),
            "fair_value": round(fair_value, 2),
            "upside_pct": round(upside, 1),
            "star_rating": row.get("StarRatingM255", ""),
            "moat": row.get("EconomicMoat", ""),
            "uncertainty": row.get("AssessmentOfFairValueUncertainty", ""),
            "sector": row.get("SectorName", ""),
            "industry": row.get("IndustryName", ""),
        })

    # 上昇余地の大きい順に並べる。
    stocks.sort(key=lambda x: x["upside_pct"], reverse=True)

    # 上位100銘柄を表示する。
    print(f"\n{'='*80}")
    print("  上昇余地 上位100銘柄")
    print(f"{'='*80}\n")
    print(f"  {'順位':>4} {'コード':<8} {'会社名':<35} {'現在値':>10} {'公正価値':>10} {'上昇余地':>8} {'星':>4} {'経済的な堀':<8} {'業種':<20}")
    print(f"  {'-'*4} {'-'*8} {'-'*35} {'-'*10} {'-'*10} {'-'*8} {'-'*4} {'-'*8} {'-'*20}")

    for i, s in enumerate(stocks[:100], 1):
        print(
            f"  {i:>4} {s['ticker']:<8} {s['name'][:35]:<35} "
            f"${s['close_price']:>9,.2f} ${s['fair_value']:>9,.2f} "
            f"{s['upside_pct']:>+7.1f}% "
            f"{'★'*int(s['star_rating']) if s['star_rating'] else 'N/A':>4} "
            f"{s['moat']:<8} {s['industry'][:20]:<20}"
        )

    # 全件をCSVへ保存する。
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    csv_path = os.path.join(OUTPUT_DIR, f"morningstar_fair_value_{today}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank", "ticker", "name", "close_price", "fair_value",
            "upside_pct", "star_rating", "moat", "uncertainty", "sector", "industry"
        ])
        writer.writeheader()
        for i, s in enumerate(stocks, 1):
            writer.writerow({"rank": i, **s})

    print(f"\n  全データを保存した: {csv_path}")
    print(f"  {len(stocks)}銘柄を上昇余地順に収録した\n")

    # 集計概要
    undervalued = [s for s in stocks if s["upside_pct"] > 0]
    overvalued = [s for s in stocks if s["upside_pct"] < 0]
    print("  📊 集計概要:")
    print(f"     公正価値を下回る銘柄: {len(undervalued)}銘柄 ({len(undervalued)/len(stocks)*100:.0f}%)")
    print(f"     公正価値を上回る銘柄: {len(overvalued)}銘柄 ({len(overvalued)/len(stocks)*100:.0f}%)")
    if undervalued:
        avg_upside = sum(s["upside_pct"] for s in undervalued) / len(undervalued)
        print(f"     公正価値を下回る銘柄の平均上昇余地: +{avg_upside:.1f}%")
    if stocks:
        wide_moat_undervalued = [s for s in stocks if s["moat"] == "Wide" and s["upside_pct"] > 0]
        print(f"     Wide Moatかつ公正価値を下回る銘柄: {len(wide_moat_undervalued)}銘柄")


if __name__ == "__main__":
    main()
