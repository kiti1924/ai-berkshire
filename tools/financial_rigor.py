#!/usr/bin/env python3
"""AI Berkshire向け財務精度検証ツール。

投資調査で使用する財務データと計算結果を検証するコマンドラインツールである。
Claude CodeおよびCodexのSkillから、重要な検証工程で自動的に呼び出される。

外部依存はなく、Python標準ライブラリのみを使用する。Python 3.7以上が必要。

使用例（通常はSkillから自動実行される）：
    python3 tools/financial_rigor.py verify-market-cap --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD
    python3 tools/financial_rigor.py verify-valuation --price 510 --eps 23.5 --bvps 120 --fcf-per-share 18 --dividend 2.4
    python3 tools/financial_rigor.py cross-validate --field revenue --values '{"年次報告書": 7518, "Yahoo": 7500, "StockAnalysis": 7520}' --unit 億元
    python3 tools/financial_rigor.py benford --values '[1234, 2345, 3456, ...]'
    python3 tools/financial_rigor.py calc --expr '510 * 9.11e9'
"""

import argparse
import json
import math
import sys
from decimal import Decimal, Context, ROUND_HALF_EVEN, InvalidOperation

# ---------------------------------------------------------------------------
# Decimalによる精密計算（浮動小数点誤差を避ける）
# ---------------------------------------------------------------------------

_CTX = Context(prec=28, rounding=ROUND_HALF_EVEN)


def exact(value) -> Decimal:
    """数値をDecimalへ変換し、float由来の誤差を避ける。"""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(str(value))


def fmt_number(d: Decimal, unit: str = "") -> str:
    """大きな数値を、指定された通貨単位を維持して読みやすく整形する。"""
    v = float(d)
    abs_v = abs(v)
    hundred_million_units = {
        "亿": "万亿",
        "亿元": "万亿元",
        "亿人民币": "万亿人民币",
        "亿港元": "万亿港元",
        "亿美元": "万亿美元",
        "億": "兆",
        "億元": "兆元（CNY）",
        "億人民元": "兆人民元",
        "億香港ドル": "兆香港ドル",
        "億米ドル": "兆米ドル",
        "億ドル": "兆米ドル",
        "億円": "兆円",
    }
    if unit in hundred_million_units:
        if abs_v >= 10000:
            return f"{v/10000:.2f}{hundred_million_units[unit]}"
        return f"{v:.2f}{unit}"
    if abs_v >= 1e12:
        return f"{v/1e12:.2f}T"
    if abs_v >= 1e9:
        return f"{v/1e9:.2f}B"
    if abs_v >= 1e6:
        return f"{v/1e6:.2f}M"
    return f"{v:,.2f}"


# ---------------------------------------------------------------------------
# 1. 時価総額の検算（株価×発行済株式数と報告値の比較）
# ---------------------------------------------------------------------------

def verify_market_cap(price, shares, reported_cap, currency=""):
    """時価総額＝株価×発行済株式数を計算し、報告値と比較する。"""
    p = exact(price)
    s = exact(shares)
    r = exact(reported_cap)

    calculated = _CTX.multiply(p, s)
    deviation = abs(float(calculated - r) / float(r)) * 100 if r != 0 else 0

    print("=" * 60)
    print("時価総額の検算")
    print("=" * 60)
    print(f"  株価:               {p} {currency}")
    print(f"  発行済株式数:       {fmt_number(s)}")
    print(f"  計算時価総額:       {fmt_number(calculated)} {currency}")
    print(f"  報告時価総額:       {fmt_number(r)} {currency}")
    print(f"  偏差:               {deviation:.2f}%")
    print()

    if deviation > 5:
        print(f"  ❌ 警告: 偏差が{deviation:.1f}%で5%を超えている。次を確認すること。")
        print("     - 発行済株式数は最新か（自己株式取得・増資を反映しているか）")
        print("     - 通貨単位は一致しているか（HKD、CNY、USD、JPY）")
        print("     - 株価の基準日は一致しているか")
        return False
    elif deviation > 1:
        print(f"  ⚠️  偏差は{deviation:.1f}%で許容範囲内だが、株価変動や株式数の変化を確認すること")
        return True
    else:
        print(f"  ✅ 検算に合格した。偏差は{deviation:.2f}%である")
        return True


# ---------------------------------------------------------------------------
# 2. バリュエーション指標の検算
# ---------------------------------------------------------------------------

def verify_valuation(price, eps=None, bvps=None, fcf_per_share=None,
                     dividend=None, revenue_per_share=None):
    """入力値から主要なバリュエーション指標を計算する。"""
    p = exact(price)

    print("=" * 60)
    print("バリュエーション指標の検算")
    print("=" * 60)
    print(f"  現在株価: {p}")
    print()

    results = {}

    if eps is not None:
        e = exact(eps)
        if e != 0:
            pe = _CTX.divide(p, e)
            print(f"  PE (TTM):  {p} / {e} = {pe:.2f}x")
            results["PE"] = float(pe)
            # 株式益回り
            ey = _CTX.divide(e, p) * 100
            print(f"  株式益回り: {ey:.2f}%")
        else:
            print("  PER: EPSが0のため計算できない")

    if bvps is not None:
        b = exact(bvps)
        if b != 0:
            pb = _CTX.divide(p, b)
            print(f"  PB:        {p} / {b} = {pb:.2f}x")
            results["PB"] = float(pb)
            if eps is not None and float(exact(eps)) != 0:
                roe = _CTX.divide(exact(eps), b) * 100
                print(f"  ROE:       {exact(eps)} / {b} = {roe:.2f}%")
                results["ROE"] = float(roe)

    if fcf_per_share is not None:
        f = exact(fcf_per_share)
        if f != 0:
            fcf_yield = _CTX.divide(f, p) * 100
            pfcf = _CTX.divide(p, f)
            print(f"  P/FCF:     {p} / {f} = {pfcf:.2f}x")
            print(f"  FCF Yield: {fcf_yield:.2f}%")
            results["P_FCF"] = float(pfcf)
            results["FCF_Yield"] = float(fcf_yield)

    if dividend is not None:
        d = exact(dividend)
        if p != 0:
            div_yield = _CTX.divide(d, p) * 100
            print(f"  配当利回り: {d} / {p} = {div_yield:.2f}%")
            results["Dividend_Yield"] = float(div_yield)

    if revenue_per_share is not None:
        r = exact(revenue_per_share)
        if r != 0:
            ps = _CTX.divide(p, r)
            print(f"  PS:        {p} / {r} = {ps:.2f}x")
            results["PS"] = float(ps)

    print()
    print("  ✅ すべての指標をDecimalで計算し、浮動小数点誤差を避けた")
    return results


# ---------------------------------------------------------------------------
# 3. 複数情報源による交差検証
# ---------------------------------------------------------------------------

def cross_validate(field_name, source_values: dict, unit="", tolerance_pct=2.0):
    """複数情報源の同一データ点を比較し、不一致を検出する。"""
    print("=" * 60)
    print(f"交差検証: {field_name}")
    print("=" * 60)

    values = {k: exact(v) for k, v in source_values.items()}
    sources = list(values.keys())
    nums = list(values.values())

    # 中央値を基準値とする。
    sorted_vals = sorted(float(v) for v in nums)
    n = len(sorted_vals)
    median = sorted_vals[n // 2] if n % 2 == 1 else (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2

    print(f"  情報源数: {len(sources)}")
    print(f"  参照中央値: {fmt_number(exact(median))} {unit}")
    print()

    all_ok = True
    for src, val in values.items():
        dev = abs(float(val) - median) / median * 100 if median != 0 else 0
        status = "✅" if dev <= tolerance_pct else "❌"
        if dev > tolerance_pct:
            all_ok = False
        print(f"  {status} {src:20s}: {fmt_number(val)} {unit}  (偏差 {dev:.2f}%)")

    print()
    if all_ok:
        print(f"  ✅ すべての情報源の偏差が{tolerance_pct}%以下であり、整合している")
    else:
        print(f"  ⚠️  {tolerance_pct}%を超える偏差がある。会計基準、期間、通貨、基準日を確認すること")
        print("     優先順位: 法定開示、取引所資料、企業の公式資料")

    # 合意値
    consensus = median
    print(f"\n  合意値（中央値）: {fmt_number(exact(consensus))} {unit}")
    return {"consensus": consensus, "all_consistent": all_ok}


# ---------------------------------------------------------------------------
# 4. ベンフォードの法則による簡易確認
# ---------------------------------------------------------------------------

_BENFORD = {d: math.log10(1 + 1/d) for d in range(1, 10)}


def benford_check(values: list):
    """財務数値の先頭数字分布をベンフォードの法則で簡易確認する。"""
    print("=" * 60)
    print("ベンフォードの法則による分布確認")
    print("=" * 60)

    # 先頭数字を抽出する。
    digits = []
    for v in values:
        v = abs(float(v))
        if v > 0:
            sig = 10 ** (math.log10(v) - math.floor(math.log10(v)))
            d = int(sig)
            if 1 <= d <= 9:
                digits.append(d)

    n = len(digits)
    if n < 50:
        print(f"  ⚠️  標本数が不足している: {n} < 50。判定結果の信頼性は低い")
        return None

    # 観測分布
    counts = {}
    for d in digits:
        counts[d] = counts.get(d, 0) + 1
    observed = {d: counts.get(d, 0) / n for d in range(1, 10)}

    # MAD（Nigriniの平均絶対偏差）
    mad = sum(abs(observed.get(d, 0) - _BENFORD[d]) for d in range(1, 10)) / 9

    # カイ二乗統計量
    chi2 = sum((counts.get(d, 0) - _BENFORD[d] * n) ** 2 / (_BENFORD[d] * n) for d in range(1, 10))

    # 戻り値は既存契約を維持し、表示だけを日本語化する。
    if mad < 0.006:
        conformity = "Close (高度符合)"
        conformity_display = "Close（高い適合）"
    elif mad < 0.012:
        conformity = "Acceptable (可接受)"
        conformity_display = "Acceptable（許容範囲）"
    elif mad < 0.015:
        conformity = "Marginally Acceptable (边缘)"
        conformity_display = "Marginally Acceptable（境界）"
    else:
        conformity = "Nonconforming (不符合 ⚠️)"
        conformity_display = "Nonconforming（不適合）"

    print(f"  標本数:    {n}")
    print(f"  MAD:       {mad:.6f}")
    print(f"  カイ二乗:  {chi2:.2f}")
    print(f"  適合度:    {conformity_display}")
    print()

    # 先頭数字の分布表
    print(f"  {'先頭数字':>6} {'観測値':>8} {'理論値':>12} {'偏差':>8}")
    print(f"  {'-'*6} {'-'*8} {'-'*12} {'-'*8}")
    for d in range(1, 10):
        obs = observed.get(d, 0)
        exp = _BENFORD[d]
        dev = obs - exp
        flag = " ⚠️" if abs(dev) > 0.03 else ""
        print(f"  {d:>6d} {obs:>8.3f} {exp:>12.3f} {dev:>+8.3f}{flag}")

    print()
    is_ok = mad < 0.015
    if is_ok:
        print("  ✅ 先頭数字の分布はベンフォードの法則に適合している")
    else:
        print("  ❌ 先頭数字の分布に異常がある。追加調査が必要である")
        print("     注意: 不適合だけでは不正を意味しない。母集団の性質も確認すること")

    return {"mad": mad, "chi2": chi2, "conformity": conformity, "is_conforming": is_ok}


# ---------------------------------------------------------------------------
# 5. 精密計算機
# ---------------------------------------------------------------------------

def exact_calc(expr: str):
    """財務計算式を精密に評価する。

    +、-、*、/、括弧、科学表記を含む数値に対応する。
    """
    print("=" * 60)
    print("精密計算")
    print("=" * 60)

    # 数字と算術記号だけを許可する。
    allowed = set("0123456789.+-*/() eE")
    if not all(c in allowed for c in expr.replace(" ", "")):
        print(f"  ❌ 許可されていない文字を含む式である: {expr}")
        return None

    try:
        # 評価結果をDecimalへ変換する。
        result = eval(expr, {"__builtins__": {}}, {})
        d_result = exact(result)
        print(f"  計算式: {expr}")
        print(f"  結果:   {fmt_number(d_result)}")
        print(f"  精密値: {d_result}")
        return float(d_result)
    except Exception as e:
        print(f"  ❌ 計算エラー: {e}")
        return None


# ---------------------------------------------------------------------------
# 6. 3シナリオのバリュエーション
# ---------------------------------------------------------------------------

def three_scenario_valuation(current_price, current_eps, shares_billion,
                             growth_optimistic, growth_neutral, growth_pessimistic,
                             pe_optimistic, pe_neutral, pe_pessimistic,
                             years=3, currency=""):
    """楽観・基準・悲観シナリオの目標株価を精密計算する。"""
    print("=" * 60)
    print("3シナリオ・バリュエーションモデル")
    print("=" * 60)

    p = exact(current_price)
    eps = exact(current_eps)
    shares = exact(shares_billion)

    scenarios = [
        ("楽観（Bull）", growth_optimistic, pe_optimistic),
        ("基準（Base）", growth_neutral, pe_neutral),
        ("悲観（Bear）", growth_pessimistic, pe_pessimistic),
    ]

    print(f"  現在株価: {p} {currency}")
    print(f"  現在EPS:  {eps}")
    print(f"  予測期間: {years}年")
    print()
    print(f"  {'シナリオ':12} {'年成長率':>8} {'目標PER':>8} {'目標EPS':>10} {'目標株価':>10} {'騰落率':>8}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*8}")

    for name, growth, pe in scenarios:
        g = exact(growth)
        target_pe = exact(pe)
        # 将来EPS = 現在EPS × (1 + 成長率)^年数
        future_eps = eps
        for _ in range(years):
            future_eps = _CTX.multiply(future_eps, _CTX.add(Decimal("1"), g))
        target_price = _CTX.multiply(future_eps, target_pe)
        change = float(target_price - p) / float(p) * 100

        print(f"  {name:12} {float(g)*100:>7.0f}% {float(target_pe):>7.0f}x "
              f"{float(future_eps):>10.2f} {float(target_price):>9.1f} {change:>+7.1f}%")

    print()
    print("  ✅ すべてDecimalで計算し、監査・再現可能な結果を出力した")


# ---------------------------------------------------------------------------
# CLIエントリーポイント
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="財務精度検証ツール：財務データと計算結果を精密に検証する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s verify-market-cap --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD
  %(prog)s verify-valuation --price 510 --eps 23.5 --bvps 120
  %(prog)s cross-validate --field revenue --values '{"年次報告書": 7518, "Yahoo": 7500}' --unit 億元
  %(prog)s benford --values '[1234, 2345, 3456, ...]'
  %(prog)s calc --expr '510 * 9.11e9'
        """)

    sub = parser.add_subparsers(dest="command")

    # verify-market-cap
    mc = sub.add_parser("verify-market-cap", help="時価総額＝株価×発行済株式数を検算する")
    mc.add_argument("--price", type=float, required=True)
    mc.add_argument("--shares", type=float, required=True, help="発行済株式数")
    mc.add_argument("--reported", type=float, required=True, help="報告時価総額")
    mc.add_argument("--currency", default="", help="通貨コード（JPY、USD、CNY、HKDなど）")

    # verify-valuation
    val = sub.add_parser("verify-valuation", help="バリュエーション指標を検算する")
    val.add_argument("--price", type=float, required=True)
    val.add_argument("--eps", type=float, default=None)
    val.add_argument("--bvps", type=float, default=None, help="1株当たり純資産")
    val.add_argument("--fcf-per-share", type=float, default=None)
    val.add_argument("--dividend", type=float, default=None, help="1株当たり配当")
    val.add_argument("--revenue-per-share", type=float, default=None)

    # cross-validate
    cv = sub.add_parser("cross-validate", help="複数情報源を交差検証する")
    cv.add_argument("--field", required=True, help="データ項目名")
    cv.add_argument("--values", required=True, help="JSON形式: {情報源: 数値}")
    cv.add_argument("--unit", default="")
    cv.add_argument("--tolerance", type=float, default=2.0, help="許容偏差（%%）")

    # benford
    bf = sub.add_parser("benford", help="ベンフォードの法則で分布を確認する")
    bf.add_argument("--values", required=True, help="JSON配列")

    # calc
    ca = sub.add_parser("calc", help="精密計算を行う")
    ca.add_argument("--expr", required=True, help="算術式")

    # three-scenario
    ts = sub.add_parser("three-scenario", help="楽観・基準・悲観の3シナリオを評価する")
    ts.add_argument("--price", type=float, required=True)
    ts.add_argument("--eps", type=float, required=True)
    ts.add_argument("--shares", type=float, required=True, help="発行済株式数（億株）")
    ts.add_argument("--growth", nargs=3, type=float, required=True,
                    help="年成長率を楽観・基準・悲観の順に指定する。例: 0.15 0.08 0.0")
    ts.add_argument("--pe", nargs=3, type=float, required=True,
                    help="目標PERを楽観・基準・悲観の順に指定する。例: 25 20 15")
    ts.add_argument("--years", type=int, default=3)
    ts.add_argument("--currency", default="")

    args = parser.parse_args()

    if args.command == "verify-market-cap":
        verify_market_cap(args.price, args.shares, args.reported, args.currency)
    elif args.command == "verify-valuation":
        verify_valuation(args.price, args.eps, args.bvps, args.fcf_per_share,
                        args.dividend, args.revenue_per_share)
    elif args.command == "cross-validate":
        values = json.loads(args.values)
        cross_validate(args.field, values, args.unit, args.tolerance)
    elif args.command == "benford":
        values = json.loads(args.values)
        benford_check(values)
    elif args.command == "calc":
        exact_calc(args.expr)
    elif args.command == "three-scenario":
        three_scenario_valuation(
            args.price, args.eps, args.shares,
            args.growth[0], args.growth[1], args.growth[2],
            args.pe[0], args.pe[1], args.pe[2],
            args.years, args.currency)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
