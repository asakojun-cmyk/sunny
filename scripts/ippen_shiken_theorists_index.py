#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：理論家図鑑の一覧（/theorists/）を、ラフ_1119 の05b（一覧と系譜）の型に組みかえる道具。

- 66人の名前・英語名・分野・ひとこと・過去6回の出題数は、本番の一覧のまま（似顔絵だけ img/nigaoe/ の絵に）
- 並びは指示書19番のとおり、過去6回の出題数の多い順（同じ数なら本番の番号順）。印も19番の決め方
- 系譜は、本番の「キャリア理論の系譜」「カウンセリング理論の系譜」「理論家の覚え方」への入口にする
  （ラフの6つの流れのタブの文は本番にないので入れない）
- 授業の音声はないページ

使い方: python3 scripts/ippen_shiken_theorists_index.py
"""
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402
from ippen_shiken_terms import inner, text, SUNNY, MOYAN, CLOUD  # noqa: E402
from ippen_shiken_theorists import wb_heads  # noqa: E402

ROOT = P.ROOT


def build():
    path = "theorists/index.html"
    full = os.path.join(ROOT, path)
    prod = S.prod_html(path)  # 組みかえる前の版（git）から読む。何度回しても同じ
    soup = BeautifulSoup(prod, "html.parser")
    r = P.rel_root(path)
    main = soup.select_one("main")
    people = []
    for i, li in enumerate(main.select(".theorist-list__item")):
        a = li.select_one("a")
        slug = a["href"].rstrip("/").split("/")[-1]
        num = re.search(r"No\.(\d+)", text(li.select_one(".theorist-list__number")))
        kc = li.select_one(".kako-chip")
        times = int(re.search(r"(\d+)回$", text(kc)).group(1)) if kc else 0
        people.append(dict(slug=slug, no=int(num.group(1)), times=times,
                           name=inner(li.select_one(".theorist-list__name")),
                           name_t=text(li.select_one(".theorist-list__name")),
                           en=inner(li.select_one(".theorist-list__en")),
                           field=inner(li.select_one(".theorist-list__field")),
                           one=inner(li.select_one(".theorist-list__oneliner"))))
    people.sort(key=lambda p: (-p["times"], p["no"]))

    def card(p):
        cl = f'<img src="{r}{CLOUD}" alt="">'
        if p["times"] >= 3:
            f = cl * 3 + f' よく出る・<wbr>過去6回で{p["times"]}回'
        elif p["times"] >= 1:
            f = cl * 2 + f' ときどき出る・<wbr>過去6回で{p["times"]}回'
        else:
            f = cl + " おさえて安心"
        img = (f'<span class="nf nf-card"><img src="{r}img/nigaoe/{p["slug"]}.webp" alt="{p["name_t"]}の似顔絵" loading="lazy"></span>'
               if os.path.exists(os.path.join(ROOT, f'img/nigaoe/{p["slug"]}.webp'))
               else f'<span class="nf nf-card ini" aria-hidden="true">{p["name_t"][:1]}</span>')
        return (f'<li><a href="/theorists/{p["slug"]}/">{img}<span class="no">No.{p["no"]:02d}</span><b>{p["name"]}</b>'
                f'<span class="en">{p["en"]}</span><span class="fd">{p["field"]}</span><span class="o">{p["one"]}</span>'
                f'<span class="f">{f}</span></a></li>')

    lede = main.select_one(".section-header__lede")
    hero = f"""<section class="lst x-uhero"><div class="w">
  <a class="x-step-tag" href="/exam/#s2">勉強の道 STEP2 ことばと理論</a>
  <p class="eye">キャリアコンサルタント学科試験に出る理論家・人物</p>
  <h1><span class="h1-kw">キャリコン試験の理論家一覧</span>理論家図鑑<span class="nw">（{len(people)}人）</span></h1>
  <p class="lede2">{inner(lede)}</p>
  <div class="sunline"><img src="{r}{SUNNY}" alt="サニー先生"><p class="sb"><span class="who">サニー先生</span>名前を押すと、その人のページへ。つながりは下の系譜で見られるよ。</p></div>
</div></section>"""
    find = f"""<section class="sec2 green x-find" aria-label="理論家をさがす"><div class="w">
  <form class="zfind" role="search" action="/search/" method="get" style="padding:20px 0 0"><div class="box"><input type="search" name="q" aria-label="理論家をさがす" placeholder="名前・キーワードでさがす"><button type="submit">さがす</button></div><a class="tl" href="#keifu">系譜で見る</a></form>
  <p class="frule">印は過去6回（第27〜32回）の出題数から：3回以上 よく出る／1〜2回 ときどき出る／0回 おさえて安心。並びは、出題数の多い順です</p>
</div></section>"""
    talk = main.select_one(".chara-after")
    pair = ""
    if talk is not None:
        bs = talk.select(".chara-guide__bubble")
        pair = (f'<div class="pair after2"><div class="pm"><p><span class="who">モヤン</span>{inner(bs[0])}</p><img src="{r}{MOYAN}" alt="モヤン"></div>'
                f'<div class="ps"><img src="{r}{SUNNY}" alt="サニー先生"><p><span class="who">サニー先生</span>{inner(bs[1])}</p></div></div>')
    note = main.select_one(".page-guide")
    note_t = ""
    if note is not None:
        m = re.match(r"※?(.*?イメージイラストです)", text(note))
        note_t = f'<p class="note2" style="margin-top:14px">{m.group(1)}。</p>' if m else ""
    ichiran = f"""<section class="lst x-ichiran"><div class="w">
  <ul class="tgrid">{''.join(card(p) for p in people)}</ul>
  {note_t}
  {pair}
</div></section>"""
    chips = main.select(".guide-chips li a")
    cards = "".join(
        f'<a class="kcard" href="/theorists/{a["href"].strip("./")}/"><small>{inner(a.small)}</small><b>{inner(a.b)}</b><span class="tl">ひらく</span></a>'
        for a in chips)
    keifu = f"""<section class="sec2 sky" id="keifu"><div class="w">
  <p class="eye">理論家の系譜</p>
  <h2>誰から誰へ、つながりで覚える</h2>
  <div class="kcards">{cards}</div>
</div></section>"""

    rough = S.rough_body("05b", path)
    tail = rough[rough.index('<section class="sec2 gara" id="tsugi">'):]
    tail, _s = S.split_scripts(tail)
    tail = S.link_items(tail)
    body = f"""@@TOP@@
@@MAIN@@
{hero}
{find}
{ichiran}
{keifu}
{tail.split('@@END@@')[0].rstrip()}
@@/MAIN@@
@@END@@
"""
    js = [f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>']
    body = body.replace("@@END@@\n", "@@END@@\n" + "\n".join(js) + "\n")
    body = wb_heads(body)  # 見出しの改行を意味の切れ目で（1文字落ちをなくす）
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("理論家図鑑", None)]

    def ld_fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s","item":"https://carepicnic.com%s"}' % (
                    i + 1, n, h or P.url_of(path)) for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out

    out = S.page(path, prod, body, cat="05b", crumb=crumb, extra_css=("shiken/05b-plus.css",), ld_fix=ld_fix)
    # 本番の66人へのリンクがぜんぶ残っているか
    old = {a["href"].rstrip("/").split("/")[-1] for a in main.select(".theorist-list__item a")}
    new = set(re.findall(r'href="/theorists/([a-z0-9-]+)/"', out))
    S.check(path, out)
    print(f"   理論家 {len(people)}人・本番の一覧からなくなった人：{sorted(old - new) or 'なし'}")


if __name__ == "__main__":
    S.prepare()
    build()
