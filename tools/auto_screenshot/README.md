# 自動スクリーンショットツール

指定した**枚数**・**間隔**でスクリーンショットを自動で撮影します。AIは使っていません（Python のみ）。

## インストール

Python 3.8 以上が必要です。

```bash
# PCの画面を撮る場合
pip install mss

# Webページを撮る場合
pip install playwright
playwright install chromium
```

## 使い方

```bash
# PCの画面を 5秒間隔で 10枚
python auto_screenshot.py -n 10 -i 5

# 3秒待ってから、メインモニターだけを 1分間隔で 30枚
python auto_screenshot.py -n 30 -i 60 --delay 3 --monitor 1

# Webページを 10分間隔で 6枚（毎回再読み込み・ページ全体）
python auto_screenshot.py -n 6 -i 600 --url https://example.com --full-page
```

画像は `screenshots/shot_01_20261004_153000.png` のような名前で保存されます。

## オプション

| オプション | 内容 | 既定値 |
|---|---|---|
| `-n`, `--count` | 撮影枚数（必須） | — |
| `-i`, `--interval` | 撮影間隔・秒（必須、小数可） | — |
| `-o`, `--outdir` | 保存先フォルダ | `screenshots` |
| `--delay` | 1枚目までの待ち時間（秒） | `0` |
| `--monitor` | 画面モード: 0=全モニター, 1=メイン, 2〜=サブ | `0` |
| `--url` | 指定するとWebモードになる | — |
| `--full-page` | Webモード: ページ全体を撮影 | オフ |
| `--width` / `--height` | Webモード: ブラウザの表示サイズ | `1280` / `800` |
| `--no-reload` | Webモード: 2枚目以降に再読み込みしない | オフ |

撮影間隔は開始時刻を基準に補正しているため、撮影に時間がかかっても間隔がずれていきません。途中で止めるには `Ctrl+C` を押してください。
