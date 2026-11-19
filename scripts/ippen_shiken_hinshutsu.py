#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：よく出る用語（/hinshutsu/）を、ラフ_1119 の10（試験の道具）の型に組む道具。

- 「よく出る」は指示書19番の決まり1つ：過去6回（第27〜32回）で3回以上。162語の中から数え直す
  （本番の一覧は ☀️☀️☀️ の目安で59語。回数は各用語ページの札。scripts/ippen_shiken_termdata.py）
- 名前・ひとこと・リンク先は本番のことば図鑑の一覧の文のまま。サニー先生とモヤンの言葉、1問1答・出題傾向・ことば図鑑への案内も本番の文
- ラフの道具の棚（上の帯・下の4つの棚）は、どれも本番のページの名前と、そのページに書いてある数だけ
- 頭（title・説明文・構造化データ）は本番のまま。語の数だけ数え直した数にする

使い方: /Users/iwawakiasako/voicevox-engine/venv/bin/python scripts/ippen_shiken_hinshutsu.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402
import ippen_shiken_termdata as T  # noqa: E402

ROOT = P.ROOT
PATH = "hinshutsu/index.html"
GROUPS = [("g1", "genre-1"), ("g2", "genre-3"), ("g3", "genre-2"), ("g4", "genre-4")]  # ラフの並び（本番のよく出る用語と同じ）


def prod_html():
    s = open(os.path.join(ROOT, PATH), encoding="utf-8").read()
    if "section-header__lede" in s:
        return s
    return subprocess.run(["git", "-C", ROOT, "show", f"{T.BASE}:{PATH}"], capture_output=True, text=True, check=True).stdout


def cells(n):
    return "".join(f'<i class="{"f" if i < n else ""}"></i>' for i in range(6))


def build():
    S.prepare()
    prod = prod_html()
    data = [x for x in T.collect() if x["n"] >= 3]
    N = len(data)
    old_n = re.search(r"(\d+)語だけを集めました", re.sub(r"<wbr>", "", prod)).group(1)

    # ---- 一覧（分野ごと）
    secs = []
    chips = [f'<button type="button" class="on" data-f="all">ぜんぶ<span class="num">{N}</span></button>']
    for g, gid in GROUPS:
        items = [x for x in data if x["gid"] == gid]
        name = T.GENRES[gid]
        chips.append(f'<button type="button" data-f="{g}">{name}<span class="num">{len(items)}</span></button>')
        lis = "".join(
            f'<li class="tm" data-g="{g}" data-k="{x["n"]}" data-n="{x["no"]}" data-t="{x["name_t"]} {x["yomi_t"]} {x["one_t"]} {x["text"]}">'
            f'<a href="{x["href"]}"><span class="tt"><span data-b>{x["name"]}</span><span class="kk" title="過去6回の学科試験で出てきた回数">'
            f'<span class="cells" aria-hidden="true">{cells(x["n"])}</span>過去6回で<span data-b class="num">{x["n"]}</span>回</span></span>'
            f'<span class="one">{x["one"]}</span></a></li>' for x in items)
        secs.append(f'<section class="grp" id="{g}" data-g="{g}"><h2 class="pw">{name}<small>{len(items)}語</small></h2><ol class="tms">{lis}</ol></section>')
    lst = (f'<div class="list"><div class="w" id="lw">\n' + "\n".join(secs) +
           '\n<p class="kazu">「過去6回で◯回」は、過去6回の学科試験で実際に出てきた回数です。「よく出る」は3回以上、「ときどき出る」は1〜2回、「おさえて安心」は0回です。</p>'
           '\n<p class="none" id="none" hidden><a href="/terms/">ことば図鑑の162語からさがす →</a></p>\n</div></div>')

    body = S.rough_body("10", PATH)
    body = re.sub(r'<main class="list">.*?</main>', lambda m: lst, body, count=1, flags=re.S)
    body = re.sub(r'<div class="fchips"[^>]*>.*?</div>',
                  lambda m: f'<div class="fchips" role="group" aria-label="分野でしぼる">{"".join(chips)}</div>', body, count=1, flags=re.S)
    body = re.sub(r'<span data-b id="cn">\d+</span>', f'<span data-b id="cn">{N}</span>', body)
    body = re.sub(r'<span data-b class="mark">\d+語だけ</span>', f'<span data-b class="mark">{N}語だけ</span>', body)
    body = body.replace("<small>よく出る47語だけ</small>", f"<small>よく出る{N}語だけ</small>")
    body = body.replace("querySelector('main.list')", "querySelector('.list')")
    # サニー先生とモヤン（本番の文）
    bubbles = re.findall(r'<p class="chara-guide__bubble">(.*?)</p>', prod, re.S)
    body = re.sub(r'(<div class="ps"><img[^>]*><p><span class="who">サニー先生</span>).*?(</p></div>)',
                  lambda m: m.group(1) + bubbles[0] + m.group(2), body, count=1, flags=re.S)
    body = re.sub(r'(<div class="pm"><p><span class="who">モヤン</span>).*?(</p>)',
                  lambda m: m.group(1) + bubbles[1] + m.group(2), body, count=1, flags=re.S)
    # 一番下の帯：次の STEP の札（ラフは空だった）
    body = body.replace('<p class="go"><a href="/exam/#s3">&nbsp;→</a></p>',
                        '<p class="go"><a href="/exam/#s3"><span class="x-step-tag">勉強の道 STEP3 法律・制度・白書</span>&nbsp;→</a></p>')
    svg_m = re.search(r'<svg width="0".*?</svg>', body, re.S)
    if not svg_m and "<svg" in S.rough_html("10").split("</head>", 1)[1][:400]:
        pass
    head_part, end_part = body.split("@@END@@", 1)
    body = head_part
    _, scripts = S.split_scripts(end_part)  # ラフのしぼりこみ・並べかえ・上に貼りつく帯のスクリプト
    tail_js = "\n".join(scripts + [f'<script src="../js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
                                   '<script src="../js/reveal.js?v=2026.1018b" defer></script>',
                                   '<script src="../js/term-hints.js?v=v2026.1018" defer></script>'])
    body = body.rstrip() + "\n@@END@@\n" + tail_js + "\n"

    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("試験の道具", None), ("よく出る用語", None)]

    def ld_fix(ld):
        out = []
        for j in ld:
            j = j.replace(f"{old_n}語", f"{N}語")
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s"%s}' % (
                    i + 1, n, (', "item":"https://carepicnic.com%s"' % (h or P.url_of(PATH))) if (h or i == len(crumb) - 1) else "")
                    for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out

    prod_n = prod.replace(f"{old_n}語", f"{N}語")  # title・説明文・OGP の語の数
    out = S.page(PATH, prod_n, body, cat="10", crumb=crumb, extra_css=("shiken/10-plus.css",), ld_fix=ld_fix)
    S.check(PATH, out)
    print(f"   よく出る（3回以上）：{N}語（本番の一覧は {old_n}語）")
    old = set(re.findall(r'href="\.\./terms/([^/]+)/"', prod.split('class="term-category"', 1)[1].split('chara-after')[0]))
    new = {x["href"].split("/")[2] for x in data}
    print("   本番にあって外れた語：", sorted(old - new))
    print("   新しく入った語：", sorted(new - old))
    lost = [t for t in T.lost_sentences(prod, out) if not re.match(r"TERM \d+", t)]
    gone = {x["one_t"] for x in T.collect() if x["n"] < 3} | {x["name_t"] for x in T.collect() if x["n"] < 3}
    print("   本番の文で、新しいページに見つからない文（外れた語の名前・ひとことと TERM 番号を除く）：")
    for t in lost:
        if not any(t.replace(" ", "") in g.replace(" ", "") for g in gone):
            print("     -", t[:120])


if __name__ == "__main__":
    build()
