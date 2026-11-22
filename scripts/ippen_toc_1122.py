#!/usr/bin/env python3
"""目次の段を、上の緑の段の続きにする（2026-11-22）。

ちゃん 11/22「目次のところの白い背景は緑の延長でいいと思う。全ページ対応して。目次のボックスは白にして。」

やること（言葉は変えない）
- <section id="mokuji"> を、目次の箱（<nav>）のすぐあとで2つに分ける。
  箱までは緑（上の「答え」の段の続き）で、下に波をつけて終わる。はじめの文・更新日・広告の案内から下は
  <section class="sec2 mokuji-tsuzuki">（白）に入れ、今までどおりの見た目にする。
- 上の緑の段（#kotae）の波は外し、同じ波を目次の段の下に付ける。
- 目次の箱（.toc）は白にする。
- <style id="toc1122"> を1つ足す（あれば入れかえる）。何度かけても同じ結果になる。

ページを作り直す台本を流したあとに、ippen_brk_1122.py とあわせて通す：
使い方: python3 scripts/ippen_toc_1122.py [ページ …]（なければ下の PAGES）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ippen_brk_1122 import PAGES  # noqa: E402

GREEN = "#EEF4D6"
WAVE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 40' "
        "preserveAspectRatio='none'%3E%3Cpath d='M0 24 Q100 6 200 24 T400 24 T600 24 T800 24 T1000 24 T1200 24 "
        "V40 H0 Z' fill='%23ECF0D8'/%3E%3C/svg%3E\")")
CSS = (
    '<style id="toc1122">'
    "/* 11/22 目次の段は上の緑の続き・目次の箱は白（scripts/ippen_toc_1122.py） */"
    # 11/22 ちゃん「リード分まで緑延長していいと思う」→ はじめの文の段（.mokuji-tsuzuki）まで緑・波はその下
    f"body.kata section.sec2#mokuji{{background:{GREEN}!important;padding-top:8px!important;padding-bottom:40px!important}}"
    # display:flow-root＝はじめの文の上の余白が段の外にはみ出して白いすき間になるのを防ぐ
    f"body.kata section.sec2.mokuji-tsuzuki{{display:flow-root;background:{GREEN}!important;padding-top:0!important;padding-bottom:64px!important}}"
    # 次が水色（sky）の段なら、水色の段が自分の波を上に出すので、緑の波は出さない（2重にしない）
    "body.kata section.sec2.mokuji-tsuzuki:has(+section.sky)::after{content:none!important}"
    "body.kata section.sec2.green#kotae::after{content:none!important}"
    "body.kata section.sec2.mokuji-tsuzuki::after{position:absolute;left:0;right:0;height:40px;z-index:2;pointer-events:none;"
    f"content:\"\"!important;background:no-repeat {WAVE}!important;background-size:100% 40px!important;"
    "bottom:-39px;top:auto;transform:scaleY(-1)}"
    "body.kata #mokuji .toc{background:#fff!important}"
    "body.kata section.sec2.mokuji-tsuzuki+section.sec2:not(.sky){padding-top:64px!important}"
    "@media (max-width:760px){"
    "body.kata section.sec2#mokuji{padding-bottom:32px!important}"
    "body.kata section.sec2.mokuji-tsuzuki{padding-bottom:44px!important}"
    "body.kata section.sec2.mokuji-tsuzuki::after{height:24px;background-size:100% 24px!important;bottom:-23px}"
    "body.kata section.sec2.mokuji-tsuzuki+section.sec2:not(.sky){padding-top:48px!important}"
    "}"
    "</style>"
)
SPLIT = '</nav>\n</div></section>\n<section class="sec2 mokuji-tsuzuki"><div class="w nar">'


def apply(html):
    m = re.search(r'<section class="sec2" id="mokuji">(.*?)</section>', html, re.S)
    if not m:
        return html, "目次なし"
    note = "分け済み"
    if "mokuji-tsuzuki" not in html:
        body = m.group(1)
        i = body.find("</nav>")
        rest = body[i + 6:]
        if i < 0 or not re.sub(r"<[^>]+>|\s", "", rest):
            note = "箱のあとが空（分けない）"
        else:
            new_body = body[:i] + SPLIT + rest
            html = html[:m.start(1)] + new_body + html[m.end(1):]
            note = "分けた"
    if 'id="toc1122"' in html:
        html = re.sub(r'<style id="toc1122">.*?</style>', lambda _: CSS, html, count=1, flags=re.S)
    else:
        html = html.replace("</head>", CSS + "\n</head>", 1)
    return html, note


def main():
    for f in sys.argv[1:] or PAGES:
        p = f if os.path.isabs(f) else os.path.join(ROOT, f)
        s = open(p, encoding="utf-8").read()
        new, note = apply(s)
        if new != s:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
        print(f"{f}: {note}{'（変わりなし）' if new == s else ''}")


if __name__ == "__main__":
    main()
