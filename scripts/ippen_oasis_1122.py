#!/usr/bin/env python3
"""「キャリア・オアシス」に公式サイトのリンクを付ける（2026-11-22）。

ちゃん 11/22「キャリアオアシスのリンクも貼ってあげて」
- 公式サイト https://career-oasis.jp/ （11/22 に開けること・題名「キャリア・オアシス」を確かめた。
  利用規約の運営＝株式会社志木サテライトオフィス・ビジネスセンターと一般社団法人地域連携プラットフォーム）
- 段（<section>）ごとに、最初に出てくる1か所だけをリンクにする。すでに <a> の中ならさわらない。
- 何度かけても同じ（その段にリンクがあればさわらない）。ippen_brk_1122.py のあとに通す。
使い方: python3 scripts/ippen_oasis_1122.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://career-oasis.jp/"
PAGES = ["schools/chiiki-renkei-platform/index.html", "school-reviews/chiiki-renkei-platform/index.html",
         "schools/compare/index.html", "school-guides/dokugaku/index.html"]
NAME = re.compile(r'(?:<span class="kn">)?キャリア・(?:</span>)?(?:<wbr/?>)?(?:<span class="kn">)?オアシス(?:</span>)?')


def in_link(s, pos):
    a = s.rfind("<a ", 0, pos)
    return a != -1 and s.find("</a>", a) > pos


def apply(html):
    body_at = html.find("<body")
    out, last, n = [], 0, 0
    for sec in re.finditer(r"<section\b.*?</section>", html[body_at:], re.S):
        s0, s1 = sec.start() + body_at, sec.end() + body_at
        part = html[s0:s1]
        if URL in part:
            continue
        for m in NAME.finditer(part):
            if in_link(part, m.start()):
                continue
            link = f'<a href="{URL}" target="_blank" rel="noopener">{m.group(0)}</a>'
            out.append(html[last:s0 + m.start()])
            out.append(link)
            last = s0 + m.end()
            n += 1
            break
    out.append(html[last:])
    return "".join(out), n


def main():
    for f in PAGES:
        p = os.path.join(ROOT, f)
        s = open(p, encoding="utf-8").read()
        new, n = apply(s)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
        print(f, f"リンク +{n}")


if __name__ == "__main__":
    main()
