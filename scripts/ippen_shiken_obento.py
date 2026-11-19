#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：お弁当（理論家とお弁当のお話・8本）を、ラフ_1119 の09（お弁当）の型に組みかえる道具。

- お話の文・おかわりばなし・ことばのタネ（問題）・用語のデータ（#episode-data）は本番のまま
- 動き（js/picnic-episode.js：用語の図書館・1問ずつ・復習バスケット・会話が1言ずつ出る）は、本番の id と class を残してそのまま使う
- 授業の音声が読む所（.episode > h2・.line__msg・.okawari > h2・.okawari__card > p）と、読む人を決める
  .line--moyan などの class は残す。読む順番も変えない。書く前に「だれが・何を」を前とくらべ、ちがえば書かない
- お客さまの理論家は、似顔絵（img/nigaoe/<slug>.webp）。丸の中はあお

使い方: python3 scripts/ippen_shiken_obento.py rogers [ほかの人…]
"""
import glob
import json
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402
from ippen_shiken_terms import inner, text, spoken  # noqa: E402

ROOT = P.ROOT


def others(slug):
    """ほかのお弁当：(slug, 名前, 問い)。本番の各ページの頭から"""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "obento/*/index.html"))):
        sl = f.split("/")[-2]
        if sl == slug:
            continue
        s = open(f, encoding="utf-8").read()
        t = re.search(r"<title>(.*?)さんとお弁当", s)
        q = re.search(r'class="opening__title">.*?<span>(.*?)</span>', s, re.S)
        if t:
            out.append((sl, t.group(1), re.sub(r"<[^>]+>", "", q.group(1)) if q else ""))
    return out


def face(slug, name, r, cls="fc"):
    if os.path.exists(os.path.join(ROOT, f"img/nigaoe/{slug}.webp")):
        return f'<span class="{cls}"><img src="{r}img/nigaoe/{slug}.webp" alt="{name}さんの似顔絵"></span>'
    return f'<span class="{cls} cvn" aria-hidden="true">{name}</span>'


def build(slug):
    path = f"obento/{slug}/index.html"
    full = os.path.join(ROOT, path)
    prod = S.prod_html(path)  # 組みかえる前の版（git）から読む。何度回しても同じ
    soup = BeautifulSoup(prod, "html.parser")
    r = P.rel_root(path)
    main = soup.select_one("main")
    name = re.search(r"<title>(.*?)さんとお弁当", prod).group(1)
    op = main.select_one(".opening")
    h1 = inner(op.select_one("h1"))
    ask = inner(op.select_one(".opening__title span"))
    weather = main.select_one(".weather")
    mount = weather.select_one("[data-lesson]")
    wp = weather.find_all("p", recursive=False)
    wh2 = weather.select_one("h2")
    wspan = weather.select_one("span")
    disc = weather.select_one(".disclaimer")
    data = json.loads(soup.select_one("#episode-data").string)
    gl = data.get("glossary", {})
    qn = len(data.get("questions", []))
    gface = face(slug, name, r, "av")

    # ---- 頭（ラフ09：白い空・お弁当の舞台・芝生）
    hero = f"""<section class="obh"><div class="w">
  <div>
    <p class="eye"><span class="x-step-tag">勉強の道 STEP2 ことばと理論</span><span class="nw">理論家とお弁当</span>・<span class="nw">{text(op.select_one('.opening__title p'))}</span></p>
    <h1>{h1}</h1>
    <p class="obq pc"><span class="who">モヤン</span>{ask}</p>
    <div class="obgo"><a class="cta" href="#ch1">おはなしを読む</a><button class="play" type="button" data-lesson-go hidden><i>▶</i><span class="lb">授業をきく</span></button></div>
    <p class="obmeta"><span data-lesson-hint hidden>モヤンとサニー先生の授業が聞けるよ・</span><span class="nw">おべんとうの時間 {len(main.select('section.episode'))}つ</span>・<span class="nw">おかわりばなし</span>・<span class="nw">ことばのタネ {qn}問</span></p>
  </div>
  <div class="stage" aria-label="{text(op.select_one('img')) or op.select_one('img').get('alt', '')}">
    <img class="garl" src="{r}img/kata/sora_garland.webp" alt="" aria-hidden="true">
    <img class="c1" src="{r}img/parts/01_sky_cloud_left.webp" alt="" aria-hidden="true">
    <img class="mat" src="{r}img/parts/27_picnic_mat.webp" alt="" aria-hidden="true">
    <img class="sun" src="{r}img/kata/sunny.webp" alt="サニー先生">
    {face(slug, name, r, "guest gface")}
    <img class="moy" src="{r}img/parts/07_moyan_school_hat_crying.webp" alt="モヤン">
    <img class="box1" src="{r}img/parts/11_lunchbox.webp" alt="" aria-hidden="true">
    <img class="box2" src="{r}img/parts/11_lunchbox.webp" alt="" aria-hidden="true">
    <img class="bot" src="{r}img/parts/suito2.webp" alt="" aria-hidden="true">
    <img class="fl" src="{r}img/parts/t/23_flowers_left_group-180.webp" alt="" aria-hidden="true">
  </div>
</div><i class="hill" aria-hidden="true"></i></section>"""

    story = f"""<section class="sec2 green tenki" id="story"><div class="w nar">
  <p class="big1">{inner(wp[0]) if wp else ''}<br>{inner(wh2)}</p>
  <p class="lead3">{inner(wspan) if wspan else ''}</p>
  {f'<p class="disc">{inner(disc)}</p>' if disc else ''}
  {mount}
</div></section>"""

    # ---- お話（本番の .line をそのまま使い、ラフの吹き出しの class を足す）
    eps = main.select("section.episode")
    prog = []
    chaps = []
    for i, ep in enumerate(eps, 1):
        cid = f"ch{i}"
        h2 = ep.find("h2", recursive=False)
        chap = ep.select_one(".chapter")
        prog.append(f'<li><a href="#{cid}" data-t="{cid}">{i}<span class="lg">　{text(h2)}</span></a></li>')
        lines = ep.select_one(".lines")
        for ln in lines.select(".line"):
            c = ln.get("class")
            kind = "moyan" if "line--moyan" in c else "sunny" if "line--sunny" in c else "guest"
            ln["class"] = c + ["ln", "r" if kind == "moyan" else "l", kind]
            av = ln.select_one(".line__avatar")
            if kind == "guest":
                new = BeautifulSoup(gface, "html.parser")
            elif kind == "moyan":
                new = BeautifulSoup(f'<span class="av"><img src="{r}img/parts/07_moyan_school_hat_crying.webp" alt=""></span>', "html.parser")
            else:
                new = BeautifulSoup(f'<span class="av"><img src="{r}img/kata/sunny.webp" alt=""></span>', "html.parser")
            av.replace_with(new)
            bub = ln.select_one(".line__bubble")
            bub["class"] = bub.get("class") + ["bb"]
        for b in lines.select("button.inline-term"):
            b["class"] = b.get("class") + ["iterm"]
        lines["class"] = lines.get("class") + ["talk2"]
        after = ep.select_one(".dialogue-after")
        aft = ""
        if after is not None:
            for b in after.select("button.term"):
                b["class"] = b.get("class") + ["tbtn"]
                sp = b.find("span")
                if sp:
                    sp.name = "small"
            after["class"] = after.get("class") + ["find"]
            aft = str(after)
        chaps.append(f"""<section class="sec2 chap" id="{cid}"><div class="w nar episode">
  <p class="eye">{inner(chap)}</p>
  <h2 class="pw">{inner(h2)}</h2>
  {lines}
  {aft}
</div></section>""")
    oka = main.select_one(".okawari")
    oh2 = oka.find("h2", recursive=False)
    card = oka.select_one(".okawari__card")
    prog.append('<li><a href="#okawari" data-t="okawari">おかわり</a></li>')
    prog.append(f'<li><a href="#asobi" data-t="asobi">{qn}問</a></li>')
    prog_html = (f'<nav class="prog" aria-label="お話のどこを読んでいるか"><div class="w"><span class="pl">いま読んでいる所</span>'
                 f'<ol>{"".join(prog)}</ol></div></nav>')
    okawari = f"""<section class="sec2 sky" id="okawari"><div class="w nar okawari">
  <p class="eye c">{inner(oka.select_one('.chapter'))}</p>
  <h2 class="c pw">{inner(oh2)}</h2>
  <div class="okw">{card}<img src="{r}img/parts/11_lunchbox.webp" alt="" aria-hidden="true"></div>
</div></section>"""

    # ---- ことばのタネ（本番の id のまま。動きは picnic-episode.js）
    game = main.select_one(".game")
    gp = [p for p in game.find_all("p", recursive=False) if "chapter" not in (p.get("class") or [])]
    quiz = game.select_one("#quiz")
    quiz["class"] = quiz.get("class") + ["qz"]
    start = game.select_one("#start-quiz")
    basket = main.select_one(".basket")
    bdiv = basket.find_all("div", recursive=False)[-1]
    bchap = bdiv.select_one(".chapter")
    bchap.name = "p"
    bchap["class"] = ["eye"]
    bh = bdiv.select_one("h2")
    bh.name = "h3"
    asobi = f"""<section class="sec2" id="asobi"><div class="w nar">
  <p class="eye c">{inner(game.select_one('.chapter'))}</p>
  <h2 class="c pw">{inner(game.select_one('h2'))}</h2>
  {''.join(f'<p class="c" style="margin:10px 0 0">{inner(p)}</p>' for p in gp)}
  <div class="game2">
    <div class="qzw">{start}{quiz}</div>
    <aside class="bsk basket" aria-live="polite">{inner(bdiv)}<img src="{r}img/parts/t/11_lunchbox-136.webp" alt="" aria-hidden="true"></aside>
  </div>
</div></section>"""

    # ---- お見送り・図鑑とドリル・このお話のことば
    fw = main.select_one(".farewell")
    fl = fw.select_one(".farewell__line")
    fl["class"] = fl.get("class") + ["bye"]
    fl.select_one(".line__avatar").replace_with(BeautifulSoup(gface, "html.parser"))
    fb = fl.select_one(".line__bubble")
    fb["class"] = fb.get("class") + ["bb"]
    th = os.path.join(ROOT, f"theorists/{slug}/index.html")
    th_one = ""
    if os.path.exists(th):
        ts = BeautifulSoup(open(th, encoding="utf-8").read(), "html.parser")
        p = ts.select_one(".term-oneliner .term-prose p")
        th_one = inner(p) if p else ""
    kotoba = "".join(f'<li><a href="{g["url"]}"><span data-b>{g["label"]}</span><span>{g["short"]}</span></a></li>' for g in gl.values())
    bye = f"""<section class="sec2 gara" id="tsugi"><div class="w nar">
  <p class="eye c">{inner(fw.select_one('.chapter'))}</p>
  {fl}
  <div class="go2">
    {f'<a class="gc" href="/theorists/{slug}/">{face(slug, name, r, "cvb")}<span><span class="k">理論家図鑑</span><span data-b>{name}</span><span class="d">{th_one}</span><span class="tl">図鑑でくわしく読む</span></span></a>' if os.path.exists(th) else ''}
    <a class="gc" href="/games/quiz/"><img src="{r}img/parts/t/10_yellow_pencil-60.webp" alt="" style="width:46px;margin:0 auto"><span><span class="k">1問1答ドリル</span><span data-b>○×・4択</span><span class="d">まちがえたら、そのまま用語解説へ。</span><span class="tl">ドリルで解く</span></span></a>
  </div>
  <div class="kotoba"><p class="kh">このお話に出てきたことば</p><ul>{kotoba}</ul></div>
</div></section>"""

    # ---- ほかのお弁当
    nxa = fw.select_one(".farewell__next a")
    nxt_slug = nxa["href"].strip("./").split("/")[-1] if nxa else ""
    ol = others(slug)
    first = next((o for o in ol if o[0] == nxt_slug), ol[0] if ol else None)
    rest = [o for o in ol if o is not first]
    small = fw.select_one(".farewell__next small")
    nxt_html = ""
    if first:
        nxt_html = f"""<section class="sec2" id="next"><div class="w">
  <p class="eye c">ほかのお弁当</p>
  <h2 class="c pw">ほかの理論家とも、ランチする？</h2>
  <a class="nx1" href="/obento/{first[0]}/">{face(first[0], first[1], r, "fc big")}<span><span data-b>{first[1]}さんとランチする ▶</span><small>{first[2]}</small></span></a>
  <div class="ors" tabindex="0" aria-label="ほかのお弁当のお話（横に送れます）">{''.join(f'<a class="oc" href="/obento/{o[0]}/">{face(o[0], o[1], r)}<span><span data-b>{o[1]}さんと お弁当</span><small>{o[2]}</small></span></a>' for o in rest)}</div>
  {f'<p class="orsh">{inner(small)}</p>' if small else ''}
  <p class="c" style="margin:14px 0 0"><a class="tl" href="/obento/">お弁当のお話を、ぜんぶ見る</a></p>
</div></section>"""

    modal = main.select_one("#term-modal")
    link = modal.select_one("#term-link")
    if link is not None:
        link["href"] = "/terms/"
    modal["class"] = modal.get("class") + ["sheet"]

    rough = S.rough_body("09", path)
    i0 = rough.index('<section class="x-exit"')
    i1 = rough.index("@@END@@")
    tail = rough[i0:i1].rstrip()
    svg = re.search(r'<svg width="0".*?</svg>', S.rough_body("04", path), re.S)
    body = f"""{svg.group(0) if svg else ''}
@@TOP@@
@@MAIN@@
{hero}

{story}

{prog_html}

{''.join(chaps)}

{okawari}

{asobi}

{bye}

{nxt_html}

{tail}
{modal}
{soup.select_one('#episode-data')}
@@/MAIN@@
@@END@@
"""
    js = [f'<script src="{r}js/picnic-episode.js"></script>',
          f'<script src="{r}js/lesson-player.js?v=2026.1120" defer></script>',
          f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
          f'<script src="{r}js/obento-kata.js?v={S.CSS_VER}" defer></script>',
          f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>']
    body = body.replace("@@END@@\n", "@@END@@\n" + "\n".join(js) + "\n")
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("お弁当", "/obento/"), (f"{name}さん", None)]

    def ld_fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s","item":"https://carepicnic.com%s"}' % (
                    i + 1, n, h or P.url_of(path)) for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out

    page = path.rsplit("/", 1)[0]
    before = spoken(prod, page)
    out = S.page(path, prod, body, cat="09", crumb=crumb,
                 extra_css=("lesson-player.css", "shiken/09-plus.css"), ld_fix=ld_fix)
    after = spoken(out, page)
    if before != after:
        open(full, "w", encoding="utf-8").write(prod)
        print(f"{path}: 音声が読む段落が変わるので、書かずにもとに戻した（前{len(before)}・後{len(after)}）")
        for i, (a, b) in enumerate(zip(before, after)):
            if a != b:
                print("   ", i, a, "→", b)
                break
        return False
    S.check(path, out)
    print(f"   音声が読む段落：{len(after)}（前と同じ）")
    return True


if __name__ == "__main__":
    S.prepare()
    for s in sys.argv[1:]:
        build(s)
