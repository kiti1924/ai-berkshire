#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雪球（Xueqiu）のユーザータイムライン取得ツール。

指定ユーザーの全タイムラインを走査し、本人が記述した投稿をキーワードで抽出する。

主な機能：
  - Playwrightのログイン状態を再利用し、初回の手動ログイン結果をローカルへ保存する
  - ページ内JavaScript fetchを優先し、失敗時はAPIRequestContextへ切り替える
  - 10ページごとに進捗を保存し、中断後は保存位置から再開する
  - 2～4秒の待機、50ページごとの30秒待機、連続5回の失敗時終了で負荷を抑える
  - 採取対象ユーザー本人の記述だけを収録し、転送のみの投稿を除外する

認証情報は環境変数から受け取り、リポジトリへ保存しない：
  export XQ_PHONE=13xxxxxxxxx
  export XQ_PASSWORD=xxx
未設定の場合は初回にブラウザーを開き、QRコード、SMS、パスワードなどで手動ログインする。

使用例：
  # 段永平（ドゥアン・ヨンピン）の拼多多関連投稿
  python3 xueqiu_scraper.py \\
      --user-id 1247347556 \\
      --keywords 拼多多,PDD,Temu,黄峥 \\
      --output ../reports/拼多多/段永平雪球发言-PDD相关.md

  # 別ユーザーと別キーワード
  python3 xueqiu_scraper.py --user-id 6784593966 --keywords 茅台 --output /tmp/out.md

ログイン状態の既定パスは/tmp/xueqiu_state.jsonであり、--state-pathで変更できる。
"""

import argparse
import asyncio
import json
import os
import random
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright


def is_match(text, keywords):
    t = (text or '').lower()
    return any(k.lower() in t for k in keywords)


def parse_ts(ts):
    try:
        return datetime.fromtimestamp(int(ts) / 1000).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return str(ts)


def clean(s):
    if not s: return ''
    s = re.sub(r'<[^>]+>', '', s)
    for ent, rep in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')]:
        s = s.replace(ent, rep)
    return re.sub(r'&#\d+;', '', s).strip()


async def browser_fetch_json(page, url, timeout_s=15):
    """ページ内JS fetchを優先し、失敗時はcontext.requestへ切り替える。"""
    js = f"""
        async () => {{
            const ctl = new AbortController();
            const to = setTimeout(() => ctl.abort(), {int(timeout_s*1000)});
            try {{
                const r = await fetch({json.dumps(url)}, {{
                    headers: {{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}},
                    credentials: 'include', signal: ctl.signal
                }});
                const text = await r.text();
                clearTimeout(to);
                try {{ return JSON.parse(text); }}
                catch(e) {{ return {{_raw: text.substring(0, 300)}}; }}
            }} catch(e) {{
                clearTimeout(to);
                return {{_error: e.toString()}};
            }}
        }}
    """
    try:
        result = await asyncio.wait_for(page.evaluate(js), timeout=timeout_s + 5)
        if result and not result.get('_error') and not result.get('_raw'):
            return result
    except Exception:
        pass
    try:
        resp = await page.context.request.get(url, headers={
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://xueqiu.com/',
        }, timeout=timeout_s * 1000)
        if resp.ok:
            return await resp.json()
    except Exception:
        return None
    return None


async def verify_login(page, user_id):
    test = await browser_fetch_json(
        page,
        f'https://xueqiu.com/v4/statuses/user_timeline.json?user_id={user_id}&page=2&count=1'
    )
    return bool(test and test.get('statuses') is not None)


async def interactive_login(pw, state_path, user_id):
    phone = os.environ.get('XQ_PHONE', '')
    print("\n[ログインが必要] ブラウザーを開くため、雪球へのログインを完了すること")
    if phone:
        print(f"        環境変数 XQ_PHONE = {phone}   （パスワードはXQ_PASSWORD）")
    else:
        print("        XQ_PHONE/XQ_PASSWORDは未設定である。ブラウザーで手動ログインすること")
    browser = await pw.chromium.launch(
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
    )
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='zh-CN',
        viewport={'width': 1280, 'height': 800},
    )
    await context.add_init_script(
        "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
    )
    page = await context.new_page()
    await page.goto('https://xueqiu.com/', wait_until='domcontentloaded')
    print(">>> ブラウザーでログインすること。5秒ごとに確認し、成功後に自動継続する（最長10分）")
    ok = False
    for i in range(120):
        await asyncio.sleep(5)
        try:
            if await verify_login(page, user_id):
                ok = True
                print(f"  ✓ ログイン成功（確認{i+1}回目）")
                break
        except Exception as e:
            print(f"  ログイン確認中の例外を無視する: {e}")
        if (i + 1) % 6 == 0:
            print(f"  ...ログイン待機中（経過{(i+1)*5}秒）")
    if not ok:
        print("10分以内にログインを確認できなかったため終了する")
        await browser.close()
        return None
    await context.storage_state(path=state_path)
    print(f"ログイン状態を保存した → {state_path}")
    return browser, context, page


async def load_with_state(pw, state_path, user_id):
    if not os.path.exists(state_path):
        return None
    browser = await pw.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-blink-features=AutomationControlled'],
    )
    context = await browser.new_context(
        storage_state=state_path,
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='zh-CN',
        viewport={'width': 1280, 'height': 800},
    )
    await context.add_init_script(
        "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
    )
    page = await context.new_page()
    loaded = False
    for attempt in range(3):
        try:
            await page.goto('https://xueqiu.com/', wait_until='domcontentloaded', timeout=15000)
            loaded = True
            break
        except Exception as e:
            print(f"  トップページの読み込みに失敗した（{attempt+1}回目）: {e}")
            await asyncio.sleep(5)
    if not loaded:
        try:
            await page.goto('about:blank')
        except Exception:
            pass
    await asyncio.sleep(2)
    if await verify_login(page, user_id):
        print("✓ 保存済みのログイン状態を再利用した")
        return browser, context, page
    print("保存済みのログイン状態は失効している")
    await browser.close()
    return None


async def fetch_all_timeline(page, user_id, keywords, progress_path, dump_all_path=''):
    collected = {}
    # all_postsには本人の全投稿を保存し、オフラインでの再抽出に利用する。
    all_posts = {}
    if dump_all_path and os.path.exists(dump_all_path):
        try:
            with open(dump_all_path, encoding="utf-8") as f:
                for e in json.load(f):
                    all_posts[e['id']] = e
            print(f"  ↪ 既存の全件キャッシュを読み込んだ：{len(all_posts)}件")

        except Exception as e:
            print(f"  全件キャッシュの読み込みに失敗した: {e}")
    print("\n=== タイムライン全体を走査する ===")
    data = await browser_fetch_json(
        page,
        f'https://xueqiu.com/v4/statuses/user_timeline.json?user_id={user_id}&page=1&count=20'
    )
    if not data or data.get('error_code'):
        print(f"  1ページ目の取得に失敗した: {data}")
        return collected
    max_page = data.get('maxPage', 600)
    total = data.get('total', '?')
    print(f"  ユーザーID: {user_id} | 投稿総数: {total} | 総ページ数: {max_page}")

    total_posts = 0
    found = 0

    def process(d):
        nonlocal total_posts, found
        for post in d.get('statuses', []):
            total_posts += 1
            text = clean(post.get('text', '') or post.get('description', ''))
            title = clean(post.get('title', ''))
            rt = post.get('retweeted_status') or {}
            rt_text = clean(rt.get('text', ''))
            own_text = (text or '').strip()
            if own_text in ('', '转发微博', '轉發微博', 'Repost'):
                continue
            pid = str(post.get('id', ''))
            date = parse_ts(post.get('created_at', 0))
            entry = {'id': pid, 'date': date, 'title': title, 'text': own_text,
                     'url': f'https://xueqiu.com/{user_id}/{pid}'}
            if rt:
                rt_user = (rt.get('user') or {}).get('screen_name', '')
                entry['retweet_of'] = f'@{rt_user}: {rt_text}'
            # キーワードで絞らず全件キャッシュへ保存する。
            if dump_all_path and pid not in all_posts:
                all_posts[pid] = entry
            # キーワード一致した投稿を収集する。
            if keywords and is_match(title + ' ' + own_text, keywords):
                if pid not in collected:
                    collected[pid] = entry
                    found += 1
                    preview = own_text[:80] if own_text else (rt_text[:80] if rt_text else title[:80])
                    print(f"  ✓ [{date}] {preview}...")

    process(data)
    start_page = 2
    if os.path.exists(progress_path):
        try:
            with open(progress_path, encoding="utf-8") as f:
                prev = json.load(f)

            start_page = max(2, prev.get('next_page', 2))
            for e in prev.get('collected', []):
                collected[e['id']] = e
                found += 1
            print(f"  ↪ 再開：{start_page}ページ目から開始し、既に{found}件を収集済み")
        except Exception as e:
            print(f"  進捗ファイルの読み込みに失敗した: {e}")

    def save_progress(next_page):
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump({'next_page': next_page, 'collected': list(collected.values())},
                      f, ensure_ascii=False)
        if dump_all_path:
            with open(dump_all_path, 'w', encoding='utf-8') as f:
                json.dump(list(all_posts.values()), f, ensure_ascii=False)

    consec_fail = 0
    for p in range(start_page, max_page + 1):
        try:
            data = await browser_fetch_json(
                page,
                f'https://xueqiu.com/v4/statuses/user_timeline.json?user_id={user_id}&page={p}&count=20',
                timeout_s=15,
            )
        except Exception as e:
            print(f"  {p}ページ目で例外が発生した: {e}")
            data = None
        if not data:
            consec_fail += 1
            print(f"  {p}ページ目が無応答またはタイムアウト（連続{consec_fail}回）")
            if consec_fail >= 5:
                print("  5回連続で失敗したため、進捗を保存して終了する。再実行時に自動再開する")
                save_progress(p)
                break
            await asyncio.sleep(5 * consec_fail)
            continue
        consec_fail = 0
        if data.get('error_code'):
            print(f"  {p}ページ目のAPIエラー: {data.get('error_code')} {data.get('error_description')}")
            save_progress(p)
            break
        statuses = data.get('statuses', [])
        if not statuses:
            print(f"  {p}ページ目が空のため終了する")
            break
        prev_found = found
        process(data)
        if p % 10 == 0 or found > prev_found:
            print(f"  {p}/{max_page}ページ | 走査済み{total_posts}件 | 一致{found}件")
        if p % 10 == 0:
            save_progress(p + 1)
        if p % 50 == 0:
            print(f"  ⏸ {p}ページ目の後に30秒待機する")
            await asyncio.sleep(30)
        else:
            await asyncio.sleep(random.uniform(2.0, 4.0))
    else:
        if os.path.exists(progress_path):
            os.remove(progress_path)

    # 最後に全件キャッシュを保存する。
    if dump_all_path:
        with open(dump_all_path, 'w', encoding='utf-8') as f:
            json.dump(list(all_posts.values()), f, ensure_ascii=False)
        print(f"  全件キャッシュ → {dump_all_path}（{len(all_posts)}件）")
    print(f"\n完了：{total_posts}件を走査し、{found}件が一致した")
    return collected


def format_md(collected, user_id, keywords):
    posts = sorted(collected.values(), key=lambda x: x.get('date', ''))
    lines = [
        f"# 雪球投稿整理：ユーザー {user_id}",
        "",
        f"> **情報源**：雪球 https://xueqiu.com/u/{user_id}",
        f"> **整理日**：{datetime.now().strftime('%Y-%m-%d')}",
        f"> **収録件数**：{len(posts)}件",
        f"> **抽出キーワード**：{', '.join(keywords)}",
        f"> **取得方法**：Playwrightログイン状態 + user_timeline.json全件走査（本人の記述のみ）",
        "",
        "---",
        "",
    ]
    for i, p in enumerate(posts, 1):
        lines.append(f"## {i}. {p.get('date','?')}")
        lines.append("")
        if p.get('title'):
            lines += [f"**【{p['title']}】**", ""]
        if p.get('retweet_of'):
            lines += [f"> 転送元：{p['retweet_of']}", ""]
        if p.get('text'):
            lines.append(p['text'])
            lines.append("")
        lines += [f"出典：{p.get('url','')}", "", "---", ""]
    return '\n'.join(lines)


def parse_args():
    ap = argparse.ArgumentParser(description="雪球ユーザータイムライン取得ツール（本人の記述をキーワード抽出）")
    ap.add_argument('--user-id', type=int, help='雪球ユーザーID（プロフィールURLの数字部分）')
    ap.add_argument('--keywords', type=str, default='',
                    help='カンマ区切りのキーワード。例：拼多多,PDD,黄峥,Temu')
    ap.add_argument('--output', type=str, default='', help='Markdown出力パス')
    ap.add_argument('--raw-json', type=str, default='', help='一致した投稿のJSON出力パス（任意）')
    ap.add_argument('--state-path', type=str, default='/tmp/xueqiu_state.json',
                    help='ログイン状態の保存先（既定値 /tmp/xueqiu_state.json）')
    ap.add_argument('--dump-all', type=str, default='',
                    help='全件キャッシュの保存先。本人の全投稿を保存し、後から別キーワードで再抽出する')
    ap.add_argument('--from-cache', type=str, default='',
                    help='取得を省略し、既存の全件JSONからMarkdownを生成する（--keywordsと--outputが必要）')
    return ap.parse_args()


def filter_from_cache(cache_path, keywords, user_id):
    with open(cache_path, encoding="utf-8") as f:
        posts = json.load(f)

    out = []
    for p in posts:
        if is_match((p.get('title','') + ' ' + p.get('text','')), keywords):
            out.append(p)
    return {p['id']: p for p in out}


async def main():
    args = parse_args()
    keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]

    # オフライン抽出モード
    if args.from_cache:
        if not (keywords and args.output):
            print("--from-cacheには--keywordsと--outputの両方が必要である")
            return
        user_id = args.user_id or 0
        collected = filter_from_cache(args.from_cache, keywords, user_id)
        print(f"キャッシュ{args.from_cache}から{len(collected)}件を抽出した（キーワード: {keywords}）")
        if not collected:
            return
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(format_md(collected, user_id, keywords))
        print(f"Markdown → {args.output}")
        return

    if not args.user_id:
        print("--user-idが必要である")
        return

    progress_path = args.state_path + f'.progress.{args.user_id}'
    raw_json = args.raw_json or f'/tmp/xueqiu_{args.user_id}_raw.json'

    print("=" * 60)
    print(f"雪球取得ツール | user_id={args.user_id} | keywords={keywords} | dump_all={args.dump_all}")
    print("=" * 60)

    async with async_playwright() as pw:
        session = await load_with_state(pw, args.state_path, args.user_id)
        if not session:
            session = await interactive_login(pw, args.state_path, args.user_id)
        if not session:
            print("ログインできないため終了する")
            return
        browser, _, page = session
        collected = await fetch_all_timeline(page, args.user_id, keywords, progress_path, args.dump_all)
        await browser.close()

    print(f"\n=== 最終結果: {len(collected)}件一致 ===")
    if not collected:
        return
    with open(raw_json, 'w', encoding='utf-8') as f:
        json.dump(list(collected.values()), f, ensure_ascii=False, indent=2)
    print(f"元データJSON → {raw_json}")
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(format_md(collected, args.user_id, keywords))
        print(f"Markdown  → {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
