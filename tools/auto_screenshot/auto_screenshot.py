#!/usr/bin/env python3
"""指定した枚数・間隔でスクリーンショットを自動撮影するツール（AI不使用）。

2つのモードがあります。
  - 画面モード（デフォルト）: PCのデスクトップ画面をそのまま撮影
  - Webモード（--url 指定時）: 指定したWebページをブラウザで開いて撮影

使用例:
  # 画面を5秒間隔で10枚撮影
  python auto_screenshot.py -n 10 -i 5

  # Webページを60秒間隔で3枚、ページ全体を撮影
  python auto_screenshot.py -n 3 -i 60 --url https://example.com --full-page
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="指定枚数・指定間隔でスクリーンショットを撮影します")
    p.add_argument("-n", "--count", type=int, required=True, help="撮影する枚数")
    p.add_argument("-i", "--interval", type=float, required=True, help="撮影間隔（秒）")
    p.add_argument("-o", "--outdir", default="screenshots", help="保存先フォルダ（既定: screenshots）")
    p.add_argument("--delay", type=float, default=0, help="1枚目を撮るまでの待ち時間（秒）")
    p.add_argument("--monitor", type=int, default=0,
                   help="画面モード: 撮影するモニター番号（0=全モニター, 1=メイン, 2以降=サブ）")
    p.add_argument("--url", help="Webモード: 撮影するページのURL")
    p.add_argument("--full-page", action="store_true", help="Webモード: ページ全体を撮影")
    p.add_argument("--width", type=int, default=1280, help="Webモード: 画面幅（px）")
    p.add_argument("--height", type=int, default=800, help="Webモード: 画面高さ（px）")
    p.add_argument("--no-reload", action="store_true", help="Webモード: 2枚目以降ページを再読み込みしない")
    args = p.parse_args()
    if args.count < 1:
        p.error("--count は1以上を指定してください")
    if args.interval < 0:
        p.error("--interval は0以上を指定してください")
    return args


def make_path(outdir: Path, index: int, count: int) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    width = len(str(count))
    return outdir / f"shot_{index:0{width}d}_{stamp}.png"


def run_loop(count, interval, take):
    """take(index) を count 回、interval 秒ごとに呼ぶ。撮影時間のずれは補正する。"""
    start = time.monotonic()
    for i in range(1, count + 1):
        path = take(i)
        print(f"[{i}/{count}] 保存: {path}", flush=True)
        if i < count:
            next_at = start + interval * i
            time.sleep(max(0.0, next_at - time.monotonic()))


def capture_screen(args, outdir: Path):
    try:
        import mss
        import mss.tools
    except ImportError:
        sys.exit("mss が必要です: pip install mss")

    # mss 10 以降は mss.MSS、それ以前は mss.mss
    mss_class = getattr(mss, "MSS", None) or mss.mss
    with mss_class() as sct:
        if args.monitor >= len(sct.monitors):
            sys.exit(f"モニター番号 {args.monitor} はありません（0〜{len(sct.monitors) - 1}）")
        monitor = sct.monitors[args.monitor]

        def take(i):
            path = make_path(outdir, i, args.count)
            img = sct.grab(monitor)
            mss.tools.to_png(img.rgb, img.size, output=str(path))
            return path

        run_loop(args.count, args.interval, take)


def capture_web(args, outdir: Path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright が必要です: pip install playwright && playwright install chromium")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(args.url, wait_until="networkidle")

        def take(i):
            if i > 1 and not args.no_reload:
                page.reload(wait_until="networkidle")
            path = make_path(outdir, i, args.count)
            page.screenshot(path=str(path), full_page=args.full_page)
            return path

        try:
            run_loop(args.count, args.interval, take)
        finally:
            browser.close()


def main():
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    mode = f"Web（{args.url}）" if args.url else "画面"
    print(f"{mode}を {args.interval}秒間隔で {args.count}枚 撮影します → {outdir.resolve()}")
    print("中断するには Ctrl+C を押してください")
    if args.delay > 0:
        time.sleep(args.delay)

    try:
        if args.url:
            capture_web(args, outdir)
        else:
            capture_screen(args, outdir)
    except KeyboardInterrupt:
        print("\n中断しました")
        sys.exit(130)
    print("完了しました")


if __name__ == "__main__":
    main()
