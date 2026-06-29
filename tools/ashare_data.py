#!/usr/bin/env python3
"""中国本土A株データツール — Tencent行情とEastmoney検索・財務データ。

Claude CodeおよびCodexのSkillへ、中国本土A株の株価・財務データを提供する。
独立したモジュールとして既存ツールへ影響を与えず、curlの直接接続を使用する。

使用例（通常はSkillから自動実行される）：
    python3.11 tools/ashare_data.py quote 600519
    python3.11 tools/ashare_data.py financials 600519
    python3.11 tools/ashare_data.py valuation 600519
    python3.11 tools/ashare_data.py search 茅台

Python 3.8以上が必要であり、外部Pythonパッケージには依存しない。
"""

import argparse
import json
import os
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_EVEN

_TIMEOUT = 15


def _curl(url):
    """curl --noproxyで直接接続し、システムプロキシを経由しない。"""
    result = subprocess.run(
        ["/usr/bin/curl", "-s", "--noproxy", "*",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
         url],
        capture_output=True, timeout=_TIMEOUT,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise ConnectionError(f"リクエストに失敗した: {url}")
    # Tencent行情APIはGBK、その他はUTF-8を返す。
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return result.stdout.decode("gbk")


def _curl_json(url, params=None):
    """curlでJSONを取得する。"""
    if params:
        from urllib.parse import urlencode
        url = f"{url}?{urlencode(params)}"
    return json.loads(_curl(url))


# ---------------------------------------------------------------------------
# Tencent行情API（認証不要）
# ---------------------------------------------------------------------------

def _qq_code(code: str) -> str:
    """銘柄コードをTencent行情APIの形式へ変換する。"""
    code = code.strip().replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    if code.startswith(("6", "9", "5")):
        return f"sh{code}"
    elif code.startswith(("0", "3", "2", "1")):
        return f"sz{code}"
    elif code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sh{code}"


def _parse_qq_quote(raw: str) -> dict:
    """Tencent行情データを解析する。形式：v_shXXXXXX="field1~field2~..."; """
    start = raw.find('"')
    end = raw.rfind('"')
    if start < 0 or end <= start:
        return {}
    fields = raw[start + 1:end].split("~")
    if len(fields) < 50:
        return {}
    return {
        "name": fields[1],
        "code": fields[2],
        "price": fields[3],
        "prev_close": fields[4],
        "open": fields[5],
        "volume": fields[6],         # 売買単位（手）
        "buy_vol": fields[7],
        "sell_vol": fields[8],
        "high": fields[33] if len(fields) > 33 else fields[3],
        "low": fields[34] if len(fields) > 34 else fields[3],
        "change_pct": fields[32],
        "change_amt": fields[31],
        "turnover_amt": fields[37] if len(fields) > 37 else "-",
        "turnover_rate": fields[38] if len(fields) > 38 else "-",
        "pe": fields[39] if len(fields) > 39 else "-",
        "market_cap": fields[45] if len(fields) > 45 else "-",    # 時価総額（億元）
        "float_cap": fields[44] if len(fields) > 44 else "-",     # 流通時価総額（億元）
        "pb": fields[46] if len(fields) > 46 else "-",
        "high_52w": fields[47] if len(fields) > 47 else "-",
        "low_52w": fields[48] if len(fields) > 48 else "-",
        "total_shares": fields[38] if len(fields) > 38 else "-",  # 必要時に再計算する。
    }


def _fmt_yi(value) -> str:
    if value is None or value == "-" or value == "":
        return "-"
    try:
        v = float(value)
    except (ValueError, TypeError):
        return str(value)
    if abs(v) >= 1e8:
        return f"{v / 1e8:.2f}億"
    if abs(v) >= 1e4:
        return f"{v / 1e4:.2f}万"
    return f"{v:.2f}"


def _fmt_pct(value) -> str:
    if value is None or value == "-" or value == "":
        return "-"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


# ---------------------------------------------------------------------------
# コマンド実装
# ---------------------------------------------------------------------------

def cmd_quote(code: str):
    """リアルタイム株価のスナップショットを表示する。"""
    qq_code = _qq_code(code)
    raw = _curl(f"https://qt.gtimg.cn/q={qq_code}")
    d = _parse_qq_quote(raw)
    if not d:
        print(f"❌ 銘柄が見つからない: {code}")
        return

    print("=" * 60)
    print(f"リアルタイム株価: {d['name']} ({d['code']})")
    print("=" * 60)
    print(f"  現在値:       {d['price']} CNY")
    print(f"  騰落率:       {d['change_pct']}%")
    print(f"  騰落額:       {d['change_amt']} CNY")
    print(f"  始値:         {d['open']} CNY")
    print(f"  高値:         {d['high']} CNY")
    print(f"  安値:         {d['low']} CNY")
    print(f"  前日終値:     {d['prev_close']} CNY")
    print(f"  出来高:       {d['volume']}手")
    print(f"  売買代金:     {d['turnover_amt']}万元（CNY）")
    print(f"  時価総額:     {d['market_cap']}億元（CNY）")
    print(f"  流通時価総額: {d['float_cap']}億元（CNY）")
    print(f"  PER（動的）:  {d['pe']}")
    print(f"  PBR:          {d['pb']}")
    print(f"  売買回転率:   {d['turnover_rate']}%")
    print(f"  52週高値:     {d['high_52w']} CNY")
    print(f"  52週安値:     {d['low_52w']} CNY")


def cmd_valuation(code: str):
    """バリュエーション指標を一覧表示する。"""
    qq_code = _qq_code(code)
    raw = _curl(f"https://qt.gtimg.cn/q={qq_code}")
    d = _parse_qq_quote(raw)
    if not d:
        print(f"❌ 銘柄が見つからない: {code}")
        return

    price = d["price"]
    market_cap_yi = d["market_cap"]

    print("=" * 60)
    print(f"バリュエーション指標: {d['name']} ({d['code']})")
    print("=" * 60)
    print(f"  現在値:       {price} CNY")
    print(f"  時価総額:     {market_cap_yi}億元（CNY）")
    print(f"  流通時価総額: {d['float_cap']}億元（CNY）")
    print(f"  PER（動的）:  {d['pe']}")
    print(f"  PBR:          {d['pb']}")
    print(f"  52週高値:     {d['high_52w']} CNY")
    print(f"  52週安値:     {d['low_52w']} CNY")

    # 時価総額から発行済株式数を逆算する。
    try:
        p = Decimal(price)
        cap = Decimal(market_cap_yi) * Decimal("1e8")
        shares = cap / p
        print(f"\n  推定発行済株式数: {_fmt_yi(float(shares))}株")
        calc_cap = p * shares
        reported_cap = Decimal(market_cap_yi) * Decimal("1e8")
        diff = abs(calc_cap - reported_cap) / reported_cap * 100
        print(f"  時価総額の検算: ✅ 一致（逆算値、偏差{float(diff):.1f}%）")
    except Exception:
        pass


def cmd_financials(code: str):
    """直近5年の主要財務データを表示する。"""
    qq_code = _qq_code(code)
    raw = _curl(f"https://qt.gtimg.cn/q={qq_code}")
    d = _parse_qq_quote(raw)
    name = d.get("name", code) if d else code

    code_clean = code.strip().replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    market = "SH" if code_clean.startswith(("6", "9", "5")) else "SZ"

    # Eastmoney datacenter API（年次報告データ）
    fin_url = "https://datacenter.eastmoney.com/securities/api/data/get"
    params = {
        "type": "RPT_F10_FINANCE_MAINFINADATA",
        "sty": "ALL",
        "filter": f'(SECUCODE="{code_clean}.{market}")(REPORT_TYPE="年报")',
        "p": "1",
        "ps": "5",
        "sr": "-1",
        "st": "REPORT_DATE",
        "source": "HSF10",
        "client": "PC",
    }
    reports = []
    try:
        data = _curl_json(fin_url, params)
        reports = data.get("result", {}).get("data", [])
    except Exception:
        pass

    # 年次報告の絞り込みで取得できない場合は、報告種別の条件を外す。
    if not reports:
        params["filter"] = f'(SECUCODE="{code_clean}.{market}")'
        try:
            data = _curl_json(fin_url, params)
            reports = data.get("result", {}).get("data", [])
        except Exception:
            pass

    print("=" * 60)
    print(f"主要財務データ: {name} ({code_clean})")
    print("=" * 60)

    if not reports:
        print("  ⚠️ 財務データを取得できない。法定開示や企業公式資料で補完すること")
        return

    for r in reports[:5]:
        date = r.get("REPORT_DATE", "")[:10]
        report_name = r.get("REPORT_DATE_NAME", "")
        revenue = r.get("TOTALOPERATEREVE")
        net_profit = r.get("PARENTNETPROFIT")
        eps = r.get("EPSJB")
        bps = r.get("BPS")
        roe = r.get("ROEJQ")
        rev_growth = r.get("TOTALOPERATEREVETZ")
        profit_growth = r.get("PARENTNETPROFITTZ")

        print(f"\n  --- {date} {report_name} ---")
        if revenue is not None:
            print(f"  売上高:                   {_fmt_yi(revenue)} CNY")
        if rev_growth is not None:
            print(f"  売上高成長率:             {_fmt_pct(rev_growth)}")
        if net_profit is not None:
            print(f"  親会社株主帰属純利益:     {_fmt_yi(net_profit)} CNY")
        if profit_growth is not None:
            print(f"  純利益成長率:             {_fmt_pct(profit_growth)}")
        if eps is not None:
            print(f"  基本的1株当たり利益:      {eps} CNY")
        if bps is not None:
            print(f"  1株当たり純資産:          {bps:.2f} CNY")
        if roe is not None:
            print(f"  ROE（加重平均）:          {_fmt_pct(roe)}")


def cmd_search(keyword: str):
    """会社名またはキーワードから銘柄コードを検索する。"""
    url = "https://searchadapter.eastmoney.com/api/suggest/get"
    params = {
        "input": keyword,
        "type": "14",
        "token": "D43BF722C8E33BDC906FB84D85E326E8",
        "count": "10",
    }
    data = _curl_json(url, params)
    results = data.get("QuotationCodeTable", {}).get("Data", [])

    if not results:
        print(f"❌ '{keyword}'に一致する銘柄が見つからない")
        return

    print("=" * 60)
    print(f"検索結果: '{keyword}'")
    print("=" * 60)
    for r in results:
        code = r.get("Code", "")
        name = r.get("Name", "")
        market = r.get("MktNum", "")
        mkt_label = {"1": "上海", "2": "深圳", "3": "北京"}.get(str(market), "")
        print(f"  {code} {name} [{mkt_label}]")


# ---------------------------------------------------------------------------
# CLIエントリーポイント
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="中国本土A株データツール：Tencent行情とEastmoney財務データ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p_quote = sub.add_parser("quote", help="リアルタイム株価を表示する")
    p_quote.add_argument("code", help="銘柄コード。例: 600519")

    p_fin = sub.add_parser("financials", help="直近5年の主要財務データを表示する")
    p_fin.add_argument("code", help="銘柄コード")

    p_val = sub.add_parser("valuation", help="バリュエーション指標を表示する")
    p_val.add_argument("code", help="銘柄コード")

    p_search = sub.add_parser("search", help="銘柄コードを検索する")
    p_search.add_argument("keyword", help="会社名またはキーワード")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "quote": lambda: cmd_quote(args.code),
        "financials": lambda: cmd_financials(args.code),
        "valuation": lambda: cmd_valuation(args.code),
        "search": lambda: cmd_search(args.keyword),
    }
    cmds[args.command]()


if __name__ == "__main__":
    main()
