#!/usr/bin/env python3
"""AI Berkshire向けレポート監査ツール。

調査レポートから財務データ点の15%を抽出し、信頼できる情報源との照合結果を
判定する。すべて合格なら公開可、不一致があれば差し戻し理由を表示する。

外部依存はなく、Python標準ライブラリのみを使用する。Python 3.7以上が必要。

3段階の処理：
  1. データ点を抽出し、15%を無作為抽出する。
     python3 tools/report_audit.py extract --report reports/xxx.md

  2. 抽出した各データ点を信頼できる情報源で確認し、
     fetched_valueなどのJSONフィールドへ入力する。

  3. 確認結果を入力し、公開可／差し戻しを判定する。
     python3 tools/report_audit.py verdict --results '[...]'

  抽出結果だけを確認する場合：
     python3 tools/report_audit.py extract --report reports/xxx.md --dry-run
"""

import argparse
import json
import math
import os
import re
import sys
from decimal import Decimal, Context, ROUND_HALF_EVEN
from random import Random


def _configure_text_streams() -> None:
    """現在の端末encodingを維持しつつ、表示不能文字でCLIを停止させない。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass


_CTX = Context(prec=28, rounding=ROUND_HALF_EVEN)

# ---------------------------------------------------------------------------
# データ点抽出：Markdownレポート内の財務数値を識別する
# ---------------------------------------------------------------------------

# 中国語の旧レポートと日本語レポートを同じ抽出器で扱う。
# 長い単位を先に並べ、`亿元`を`亿`、`億香港ドル`を`億`として誤って
# 部分一致させない。抽出後も原単位を保持し、通貨を推測で変換しない。
_UNIT_PATTERN = (
    r'(?:万亿(?:人民币|港元|美元)?|亿元|亿人民币|亿港元|亿美元|'
    r'百万股|亿股|万股|亿|'
    r'億香港ドル|億米ドル|億人民元|億ドル|億円|億元|'
    r'百万株|億株|万株|千株|株|億|'
    r'兆(?:香港ドル|米ドル|人民元|ドル|円|CNY|HKD|USD|JPY)?|'
    r'[xX倍]|%|[BMT])'
)
_APPROX_PATTERN = r'[~约約]?'

# 個別パターンは外部利用との互換性のため残す。
_PATTERNS = [
    (r'([\d,，\.]+)\s*%', '%', 'percent'),
    (rf'([\d,，\.]+)\s*({_UNIT_PATTERN})', '', 'amount'),
    (r'([\d,，\.]+)\s*[xX倍]', 'x', 'multiple'),
    (r'\$\s*([\d,，\.]+)\s*([BMT])', '$', 'usd_abs'),
    (rf'\|\s*{_APPROX_PATTERN}\$?([\d,，\.]+)\s*\|', '', 'table_num'),
]

_LABEL_RE = re.compile(
    rf'(?P<label>[^\|\n：:]{{2,25}})[：:\s]+{_APPROX_PATTERN}\$?'
    rf'(?P<num>[\d,，\.]+)\s*(?P<unit>{_UNIT_PATTERN})?'
)

_TABLE_ROW_RE = re.compile(
    rf'\|\s*(?P<label>[^|]{{1,40}})\s*\|\s*{_APPROX_PATTERN}\$?'
    rf'(?P<num>[\d,，\.]+)\s*(?P<unit>{_UNIT_PATTERN})?\s*\|'
)


def _clean_num(s: str) -> float:
    """カンマまたは全角カンマを含む数値文字列をfloatへ変換する。"""
    s = s.replace(',', '').replace('，', '').strip()
    try:
        return float(s)
    except ValueError:
        return None


def _is_valid_label(label: str) -> bool:
    """財務項目として意味のあるラベルかを判定し、ノイズを除外する。"""
    label = label.strip()
    # 短すぎるラベル
    if len(label) < 2:
        return False
    # 数字または年・四半期だけのラベル
    if re.fullmatch(r'[\d\s年季度Q]+', label):
        return False
    # 記号またはMarkdown記号から始まるラベル
    if re.match(r'^[+\-\*#\|~\$>_`]', label):
        return False
    # Markdownの太字・コード記号を含むラベル
    if '**' in label or '`' in label or '__' in label:
        return False
    # 増減率だけのラベル（例：+56%、-13%）
    if re.fullmatch(r'[+\-]?\d+(\.\d+)?%', label):
        return False
    # 見出し・注記など、財務データ点ではない既知のラベル
    _SKIP = {
        '来源', '说明', '注意', '备注', '数据来源', '合计', '单位', '趋势',
        '出典', '説明', '注意', '注記', 'データ出典', '合計', '単位', '傾向',
        'sources', 'source', 'n/a', '—', '-', '/', 'total',
    }
    if label.lower() in _SKIP:
        return False
    return True


# 2列表：| ラベル | 数値 単位 |
_KV_TABLE_RE = re.compile(
    rf'^\|\s*(?P<label>[^|*\n]{{2,40}}?)\s*\|\s*{_APPROX_PATTERN}\$?'
    rf'(?P<num>[\d,，\.]+)\s*(?P<unit>{_UNIT_PATTERN})?\s*[\|（\(]'
)

# ラベル付きKV行：ラベル：数値 単位
# 日本語の仮名で始まる項目名も対象にする。
_KV_LABEL_RE = re.compile(
    rf'(?P<label>[\u3040-\u30ff\u3400-\u9fffA-Za-z][^\|\n：:*]{{1,30}})'
    rf'[：:]\s*{_APPROX_PATTERN}\$?(?P<num>[\d,，\.]+)\s*'
    rf'(?P<unit>{_UNIT_PATTERN})?'
)


def _parse_md_tables(lines: list) -> list:
    """Markdown表を解析し、行ラベル・列見出し・値・単位などを返す。"""
    results = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 表見出し行を検出する（区切り行は除く）。
        if '|' in line and not re.match(r'^\|[\-\s\|:]+\|$', line):
            headers_raw = [h.strip().strip('*_').strip() for h in line.split('|')]
            headers_raw = [h for h in headers_raw if h]
            # 次の行が区切り行であることを確認する。
            if i + 1 < len(lines) and re.match(r'^\|[\-\s\|:]+\|$', lines[i+1].strip()):
                i += 2  # 区切り行を読み飛ばす。
                # データ行を読む。
                while i < len(lines):
                    dline = lines[i].strip()
                    if not dline or not dline.startswith('|'):
                        break
                    cells = [c.strip().strip('*_~').strip() for c in dline.split('|')]
                    cells = [c for c in cells if c != '']
                    if len(cells) < 2:
                        i += 1
                        continue
                    row_label = cells[0]
                    for col_idx, cell in enumerate(cells[1:], start=1):
                        col_header = headers_raw[col_idx] if col_idx < len(headers_raw) else f'列{col_idx}'
                        # セル内の数値と単位を抽出する。
                        m = re.search(
                            rf'{_APPROX_PATTERN}\$?([\d,，\.]+)\s*({_UNIT_PATTERN})?',
                            cell,
                        )
                        if m:
                            val = _clean_num(m.group(1))
                            unit = (m.group(2) or '').strip()
                            if val and val != 0 and val < 1e15:
                                results.append((row_label, col_header, val, unit, i + 1, dline))
                    i += 1
                continue
        i += 1
    return results


def extract_data_points(md_text: str) -> list:
    """Markdownレポートから認識可能な財務データ点を抽出する。

    主に次の構造を対象とする。
      1. 複数列のMarkdown表：(行ラベル + 列見出し) → 数値
      2. コロン区切りのKV行：ラベル：数値 単位

    戻り値はid、label、reported_value、unit、raw_text、line_numberを
    持つ辞書のリストである。
    """
    points = []
    seen = set()

    def _add(label, val, unit, lineno, raw):
        label = re.sub(r'[\*_`]+', '', label).strip()
        if not _is_valid_label(label):
            return
        if val is None or val == 0 or val > 1e15:
            return
        # 年または四半期だけの値を除外する。
        if re.fullmatch(r'(20\d{2}|Q[1-4]|\d{4}\s*Q[1-4])', label.strip()):
            return
        key = f"{label}|{round(val,4)}|{unit}"
        if key in seen:
            return
        seen.add(key)
        points.append({
            'id': len(points) + 1,
            'label': label,
            'reported_value': val,
            'unit': unit,
            'raw_text': raw[:120],
            'line_number': lineno,
        })

    lines = md_text.split('\n')
    in_code = False

    # --- 1. 複数列の表 ---
    for row_label, col_header, val, unit, lineno, raw in _parse_md_tables(lines):
        # 意味のない行ラベルを除外する。
        if not _is_valid_label(row_label):
            continue
        # 増減率、説明、出典などの列は独立した検証対象にしない。
        if col_header.upper() in (
            'YOY', 'YOY增速', '增速', '同比', '变化', '趋势', '说明', '备注',
            '前年比', '増減率', '変化', '傾向', '説明', '注記', '出典', 'データ出典',
        ):
            continue
        # 列見出しが補足情報なら、行ラベルと結合する。
        if col_header and col_header != row_label:
            label = f"{row_label}・{col_header}"
        else:
            label = row_label
        _add(label, val, unit, lineno, raw)

    # --- 2. コロン区切りのKV行 ---
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code or stripped.startswith('> ') or re.match(r'^#{1,6}\s', stripped):
            continue
        if '|' in stripped:
            continue  # 表は上で処理済みである。

        for m in _KV_LABEL_RE.finditer(stripped):
            label = m.group('label')
            val = _clean_num(m.group('num'))
            unit = (m.group('unit') or '').strip()
            _add(label, val, unit, lineno, stripped)

    return points


def sample_points(points: list, ratio: float = 0.15, seed: int = None) -> list:
    """指定比率を無作為抽出する。最少3件、最多30件とする。"""
    n = max(3, min(30, math.ceil(len(points) * ratio)))
    n = min(n, len(points))
    rng = Random(seed)
    sampled = rng.sample(points, n)
    # 人手で照合しやすいよう行番号順に並べる。
    return sorted(sampled, key=lambda p: p['line_number'])


# ---------------------------------------------------------------------------
# 公開可／差し戻し判定
# ---------------------------------------------------------------------------

_TOLERANCE = 0.01   # 許容差1%


def _pct_diff(reported: float, fetched: float) -> float:
    """絶対値ベースの相対偏差を返す。"""
    if reported == 0:
        return 0.0 if fetched == 0 else float('inf')
    return abs(reported - fetched) / abs(reported)


def render_verdict(results: list, report_name: str = "") -> dict:
    """照合結果を表示し、公開可または差し戻しの判定を返す。

    各要素はid、label、reported_value、unit、fetched_value、
    fetched_sourceを持つ。任意で第2情報源のfetched_value2と
    fetched_source2を指定できる。戻り値のJSON互換キーは維持する。
    """
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    print('=' * 70)
    print(f'{BOLD}レポートデータ抽出監査：公開可／差し戻し判定{RESET}')
    if report_name:
        print(f'レポート：{report_name}')
    print('=' * 70)
    print()

    fail_items = []
    warn_items = []

    for item in results:
        label = item.get('label', '?')
        reported = float(item.get('reported_value', 0))
        unit = item.get('unit', '')
        fetched = item.get('fetched_value')
        source = item.get('fetched_source', '?')
        fetched2 = item.get('fetched_value2')
        source2 = item.get('fetched_source2', '')

        # --- 主情報源との照合 ---
        if fetched is None:
            # 確認値がない項目は合否集計から除外する。
            print(f'  ⬜ [{item["id"]:>2}] {label[:35]:35s} {reported:>12.2f} {unit}  →  [確認値なし、除外]')
            continue

        fetched = float(fetched)
        diff1 = _pct_diff(reported, fetched)

        # --- 第2情報源との照合（指定時）---
        diff2 = None
        if fetched2 is not None:
            fetched2 = float(fetched2)
            diff2 = _pct_diff(reported, fetched2)

        # 判定
        pass1 = diff1 <= _TOLERANCE
        pass2 = (diff2 is None) or (diff2 <= _TOLERANCE)

        if pass1 and pass2:
            status = f'{GREEN}✅ 合格{RESET}'
            detail = f'{source}: {fetched:.2f} (偏差 {diff1*100:.2f}%)'
            if diff2 is not None:
                detail += f'  |  {source2}: {fetched2:.2f} (偏差 {diff2*100:.2f}%)'
        elif not pass1 and not pass2:
            status = f'{RED}❌ 不合格{RESET}'
            detail = f'{source}: {fetched:.2f} (偏差 {diff1*100:.2f}%)'
            if diff2 is not None:
                detail += f'  |  {source2}: {fetched2:.2f} (偏差 {diff2*100:.2f}%)'
            fail_items.append({
                'id': item['id'],
                'label': label,
                'reported': reported,
                'unit': unit,
                'fetched': fetched,
                'source': source,
                'fetched2': fetched2,
                'source2': source2,
                'diff1_pct': round(diff1 * 100, 2),
                'diff2_pct': round(diff2 * 100, 2) if diff2 is not None else None,
                'raw_text': item.get('raw_text', ''),
                'line_number': item.get('line_number', 0),
            })
        else:
            # 一方だけが許容差内の場合は警告とし、不合格には数えない。
            status = f'{YELLOW}⚠️  要確認{RESET}'
            detail = f'{source}: {fetched:.2f} (偏差 {diff1*100:.2f}%)'
            if diff2 is not None:
                detail += f'  |  {source2}: {fetched2:.2f} (偏差 {diff2*100:.2f}%)'
            warn_items.append({
                'id': item['id'], 'label': label,
                'reported': reported, 'unit': unit,
                'diff1_pct': round(diff1 * 100, 2),
                'diff2_pct': round(diff2 * 100, 2) if diff2 is not None else None,
            })

        print(f'  {status} [{item["id"]:>2}] {label[:35]:35s}  レポート値: {reported:>12.2f} {unit}')
        print(f'              {" " * 38}{detail}')

    print()
    print('-' * 70)

    total = len([r for r in results if r.get('fetched_value') is not None])
    fail_count = len(fail_items)
    warn_count = len(warn_items)
    pass_count = total - fail_count - warn_count

    print(f'  監査件数: {total}  |  合格: {GREEN}{pass_count}{RESET}  |  要確認: {YELLOW}{warn_count}{RESET}  |  不合格: {RED}{fail_count}{RESET}')
    print()

    if fail_count == 0:
        print(f'{BOLD}{GREEN}【公開可】監査対象データはすべて合格した。{RESET}')
        verdict = 'PASS'
    else:
        print(f'{BOLD}{RED}【差し戻し】{fail_count}件が不合格である。修正後に再監査が必要である。{RESET}')
        print()
        print(f'{BOLD}差し戻し理由：{RESET}')
        for fi in fail_items:
            print(f'  ❌ {fi["line_number"]}行目 | {fi["label"]}')
            print(f'     レポート値：{fi["reported"]} {fi["unit"]}')
            print(f'     {fi["source"]}：{fi["fetched"]}  （偏差 {fi["diff1_pct"]}%）')
            if fi.get('fetched2') is not None:
                print(f'     {fi["source2"]}：{fi["fetched2"]}  （偏差 {fi["diff2_pct"]}%）')
            print(f'     原文：{fi["raw_text"][:80]}')
            print()
        verdict = 'FAIL'

    if warn_count > 0:
        print(f'{YELLOW}注意：{warn_count}件で2情報源の結果が一致しない。GAAP／Non-GAAP、換算為替、基準日の差を人手で確認すること。{RESET}')
        for wi in warn_items:
            print(f'  ⚠️  {wi["label"]}  レポート値:{wi["reported"]} {wi["unit"]}  偏差: {wi["diff1_pct"]}% / {wi["diff2_pct"]}%')

    print('=' * 70)

    return {
        'verdict': verdict,
        'pass_count': pass_count,
        'warn_count': warn_count,
        'fail_count': fail_count,
        'total': total,
        'fail_items': fail_items,
        'warn_items': warn_items,
    }


# ---------------------------------------------------------------------------
# CLIエントリーポイント
# ---------------------------------------------------------------------------

def main():
    _configure_text_streams()
    parser = argparse.ArgumentParser(
        description='レポート監査ツール：調査レポートの財務データ抽出監査',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
処理手順：

  1. データ点を抽出し、15%を無作為抽出して監査リストを表示する。
    python3 tools/report_audit.py extract --report reports/企業名/企業名-research-20260408.md

  2. 各データ点を信頼できる情報源で確認し、
     fetched_value / fetched_source / fetched_value2 / fetched_source2へ入力する。

  3. 確認結果を入力し、公開可／差し戻しを判定する。
    python3 tools/report_audit.py verdict --results '[
      {"id":1,"label":"売上高","reported_value":7518,"unit":"億元","fetched_value":7518,"fetched_source":"macrotrends","fetched_value2":7500,"fetched_source2":"stockanalysis"},
      ...
    ]'

  抽出結果だけを表示する場合：
    python3 tools/report_audit.py extract --report reports/xxx.md --dry-run

  抽出比率を指定する場合（既定値0.15）：
    python3 tools/report_audit.py extract --report reports/xxx.md --ratio 0.20

  乱数シードを固定し、同じ標本を再現する場合：
    python3 tools/report_audit.py extract --report reports/xxx.md --seed 42
        """)

    sub = parser.add_subparsers(dest='command')

    # データ抽出
    ext = sub.add_parser('extract', help='レポートからデータ点を抽出し、無作為抽出する')
    ext.add_argument('--report', required=True, help='Markdownレポートのファイルパス')
    ext.add_argument('--ratio', type=float, default=0.15, help='抽出比率。既定値は0.15')
    ext.add_argument('--seed', type=int, default=None, help='再現用の乱数シード（任意）')
    ext.add_argument('--dry-run', action='store_true', help='監査リストだけを表示し、JSONを出力しない')

    # 判定
    vrd = sub.add_parser('verdict', help='確認結果から公開可／差し戻しを判定する')
    vrd.add_argument('--results', required=True, help='fetched_valueなどを含むJSON配列')
    vrd.add_argument('--report', default='', help='表示するレポート名（任意）')
    vrd.add_argument('--output-json', action='store_true', help='判定結果をJSONで標準出力へ追加する')

    args = parser.parse_args()

    if args.command == 'extract':
        if not os.path.exists(args.report):
            print(f'❌ ファイルが存在しない: {args.report}', file=sys.stderr)
            sys.exit(1)

        with open(args.report, 'r', encoding='utf-8') as f:
            text = f.read()

        all_points = extract_data_points(text)
        sampled = sample_points(all_points, ratio=args.ratio, seed=args.seed)

        print('=' * 70)
        print('レポートデータ抽出監査リスト')
        print(f'ファイル：{args.report}')
        print(f'抽出データ点数：{len(all_points)}  |  抽出比率：{args.ratio:.0%}  |  監査件数：{len(sampled)}')
        if args.seed is not None:
            print(f'乱数シード：{args.seed}（同じ標本の再現に利用できる）')
        print('=' * 70)
        print()
        print(f'{"ID":>3}  {"行番号":>5}  {"データラベル":<35}  {"レポート値":>12}  {"単位"}')
        print(f'{"─"*3}  {"─"*5}  {"─"*35}  {"─"*12}  {"─"*6}')
        for p in sampled:
            print(f'{p["id"]:>3}  {p["line_number"]:>5}  {p["label"][:35]:<35}  {p["reported_value"]:>12.2f}  {p["unit"]}')
        print()
        print('↑ 各データ点を次の情報源などで確認し、fetched_valueへ入力すること。')
        print('  米国株：macrotrends.net（主）+ stockanalysis.com（副）')
        print('  香港株：aastocks.com（主）+ macrotrends ADR（副）')
        print('  中国本土A株：eastmoney.com（主）+ cninfo.com.cn（副）')
        print()

        if not args.dry_run:
            # 入力用JSONテンプレートを表示する。
            template = []
            for p in sampled:
                template.append({
                    'id': p['id'],
                    'label': p['label'],
                    'reported_value': p['reported_value'],
                    'unit': p['unit'],
                    'line_number': p['line_number'],
                    'raw_text': p['raw_text'],
                    'fetched_value': None,       # ← 主情報源の確認値
                    'fetched_source': '',        # ← 主情報源名
                    'fetched_value2': None,      # ← 第2情報源の確認値（任意）
                    'fetched_source2': '',       # ← 第2情報源名（任意）
                })
            print('監査リストJSON（fetched_valueを入力してverdictへ渡す）：')
            print()
            print(json.dumps(template, ensure_ascii=False, indent=2))

    elif args.command == 'verdict':
        try:
            results = json.loads(args.results)
        except json.JSONDecodeError as e:
            print(f'❌ JSONの解析に失敗した: {e}', file=sys.stderr)
            sys.exit(1)

        report_name = args.report or ''
        outcome = render_verdict(results, report_name=report_name)

        if args.output_json:
            print(json.dumps(outcome, ensure_ascii=False, indent=2))

        # 差し戻しは非ゼロ終了コードとし、CIやスクリプトで判別可能にする。
        sys.exit(0 if outcome['verdict'] == 'PASS' else 1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
