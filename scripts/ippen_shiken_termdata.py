#!/usr/bin/env python3
"""ことば図鑑の162語のデータを、本番のページから集める（04b 一覧・10 よく出る用語 で使う）。
- 名前・読み・ひとこと・さがす文・番号・ジャンル・行（あ行…）：terms/index.html の一覧
- 過去6回（第27〜32回）に出た回数：各用語ページの頭の札（kako-badge「過去6回でN回出題」）。札がなければ0回
  （一覧の「過去6回で○回」の札とも合っているかを確かめる）
- よく出るの印は指示書19番：3回以上＝よく出る／1〜2回＝ときどき出る／0回＝おさえて安心
"""
import os
import re

from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "ac71b1714"  # 試験の側を組みかえる前のコミット（本番の一覧の文はここから）
GENRES = {"genre-1": "キャリア理論", "genre-2": "カウンセリング理論", "genre-3": "カウンセリング技法", "genre-4": "制度・支援"}


def inner(el):
    return "".join(str(c) for c in el.contents) if el else ""


def level(n):
    return "よく出る" if n >= 3 else ("ときどき出る" if n >= 1 else "おさえて安心")


def page_count(href_abs):
    p = os.path.join(ROOT, href_abs.strip("/"), "index.html")
    s = open(p, encoding="utf-8").read()
    m = re.search(r'class="kako-badge"[^>]*>過去6回で<b>(\d+)</b>回出題', s) or \
        re.search(r'過去6回で <span class="num">(\d+)</span> 回', s)  # 新しい型に組みかえたページ（ippen_shiken_terms.py）
    return int(m.group(1)) if m else 0


def collect(src=None):
    """[{genre, gid, gyo, href, no, name, name_t, yomi, one, text, n, chip}]（一覧の順）"""
    s = src or open(os.path.join(ROOT, "terms/index.html"), encoding="utf-8").read()
    if 'class="term-category"' not in s:
        # 一覧を新しい型に組みかえたあとは、組みかえる前の一覧（いっぺんの共通部品を入れた版）から読む
        import subprocess
        s = subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:terms/index.html"], capture_output=True, text=True, check=True).stdout
    soup = BeautifulSoup(s, "html.parser")
    out = []
    for sec in soup.select("section.term-category"):
        gid = sec.get("id")
        gyo = None
        for li in sec.select("ul.term-list > li"):
            if "term-gyo" in (li.get("class") or []):
                gyo = li.get_text("", strip=True)
                continue
            a = li.select_one("a")
            href = a["href"].replace("../terms/", "/terms/")
            num = re.search(r"TERM\s*(\d+)", a.select_one(".term-list__number").get_text())
            chip = a.select_one(".kako-chip")
            chip_n = int(re.search(r"で(\d+)回", chip.get_text()).group(1)) if chip else None
            name = a.select_one(".term-list__name")
            out.append(dict(
                genre=GENRES[gid], gid=gid, gyo=gyo, href=href, no=num.group(1) if num else "",
                name=inner(name), name_t=name.get_text("", strip=True), yomi=inner(a.select_one(".term-list__reading")),
                yomi_t=a.select_one(".term-list__reading").get_text("", strip=True),
                one=inner(a.select_one(".term-list__oneliner")), one_t=a.select_one(".term-list__oneliner").get_text("", strip=True),
                text=li.get("data-library-text", ""), n=page_count(href), chip=chip_n))
    return out


if __name__ == "__main__":
    d = collect()
    print(len(d), "語")
    bad = [(x["name_t"], x["chip"], x["n"]) for x in d if x["chip"] is not None and x["chip"] != x["n"]]
    print("一覧の札と用語ページの札がちがう:", bad or "なし")
    from collections import Counter
    print(Counter(level(x["n"]) for x in d))
    print(Counter((x["genre"], level(x["n"])) for x in d if x["n"] >= 3))


def _main_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for w in soup.find_all("wbr"):
        w.unwrap()
    m = soup.select_one("main") or soup.body
    for x in m.select("script,style,footer,nav.bn,.kc,[aria-hidden=true]"):
        x.decompose()
    for t in m.find_all(["p", "li", "h1", "h2", "h3", "h4", "dt", "dd", "summary", "figcaption", "br", "td", "th"]):
        t.append("\n")
    return m.get_text("")


def lost_sentences(prod_html, new_html):
    """本番の <main> の文のうち、新しいページに見つからない文（記号・空白を除いてくらべる）"""
    norm = lambda t: re.sub(r"[\s　「」『』（）()、。・…!！?？〜~:：/／＼▶︎☀️🌥️🌈🌤️☂️🧺🎧\-‐]", "", t)
    new = norm(_main_text(new_html))
    out = []
    for line in _main_text(prod_html).split("\n"):
        for sent in re.split(r"(?<=[。！？])", line):
            n = norm(sent)
            if len(n) >= 6 and n not in new and sent.strip() not in out:
                out.append(sent.strip())
    return out
