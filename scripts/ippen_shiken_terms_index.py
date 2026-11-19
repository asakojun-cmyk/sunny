#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：ことば図鑑の一覧（/terms/）を、ラフ_1119 の04b（ことば図鑑の一覧）の型に組む道具。

- 162語ぜんぶ（名前・読み・ひとこと・ジャンル・行・リンク先）は本番の一覧のまま（scripts/ippen_shiken_termdata.py が集める）
- よく出るの印は指示書19番（過去6回で3回以上＝よく出る／1〜2回＝ときどき出る／0回＝おさえて安心）。回数は各用語ページの札
- さがす（js/library.js の data-library-search・data-library-book・data-library-gyo・data-library-empty）はそのまま動く
- ジャンルのボタンは、押した分野だけを見せる（スクリプトがないときは4分野とも見える）。#genre-1〜4 の着地点も残す
- ヒーローは移動図書館（x-uhero）。次の一歩は 勉強の道 STEP3。出口は比較表の30秒しぼりこみ1つ

使い方: /Users/iwawakiasako/voicevox-engine/venv/bin/python scripts/ippen_shiken_terms_index.py
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
PATH = "terms/index.html"
CLOUD = "img/parts/28_small_cloud_motif.webp"


def prod_html():
    s = open(os.path.join(ROOT, PATH), encoding="utf-8").read()
    if 'class="term-category"' in s:
        return s
    return subprocess.run(["git", "-C", ROOT, "show", f"{T.BASE}:{PATH}"], capture_output=True, text=True, check=True).stdout


def freq(n, r):
    k = 3 if n >= 3 else (2 if n >= 1 else 1)
    return (f'<span class="f"><span>{"".join(f"<img src=\"{r}{CLOUD}\" alt=\"\">" for _ in range(k))}</span>'
            f'{T.level(n)}・過去6回で{n}回</span>')


def build():
    S.prepare()
    prod = prod_html()
    r = P.rel_root(PATH)
    data = T.collect(prod)
    assert len(data) == 162, len(data)
    bubble = re.search(r'<p class="chara-guide__bubble">(.*?)</p>', prod, re.S).group(1)
    guide = re.search(r'<p class="page-guide">(.*?)</p>', prod, re.S).group(1).replace('href="../terms/', 'href="/terms/')
    trust = re.search(r'<p class="library-trust">(.*?)</p>', prod, re.S).group(1)
    trust = trust.split("｜☀️")[0]  # 「☀️＝出題ひんどの目安」は、回数で決める新しい印に置きかわったので外す
    empty = re.search(r'<p class="library-empty"[^>]*>(.*?)</p>', prod, re.S).group(1)
    story = re.search(r'<div class="library-hero__story">(.*?)</div>', prod, re.S).group(1)
    h1_old = re.search(r"<h1[^>]*>(.*?)</h1>", story, re.S).group(1)
    takara = re.sub(r"<[^>]+>", "", re.sub(r'<span class="h1-kw">.*?</span>', "", h1_old)).strip()  # 「知らない言葉は、今日見つけた宝物。」
    story_p = re.findall(r"<p>(.*?)</p>", story, re.S)
    lead = takara + "".join(re.sub(r"<br\s*/?>", "", x) for x in story_p)

    genres = list(T.GENRES.items())
    chips = "".join(f'<li><button type="button" data-genre="{gid}"{" class=\"on\"" if i == 0 else ""}>{g}</button></li>'
                    for i, (gid, g) in enumerate(genres))
    chips += ('<li><a href="/hinshutsu/">よく出る用語だけ見る</a></li>'
              '<li><a href="/theorists/">理論家（人物）から探す</a></li>')

    panels = []
    for gi, (gid, g) in enumerate(genres):
        items = [x for x in data if x["gid"] == gid]
        gyos = []
        for x in items:
            if x["gyo"] not in gyos:
                gyos.append(x["gyo"])
        kana = "".join(f'<li><a href="#{gid}-k{k}">{gy[0]}</a></li>' for k, gy in enumerate(gyos))
        lis = []
        cur = None
        for x in items:
            if x["gyo"] != cur:
                cur = x["gyo"]
                lis.append(f'<li class="kg" id="{gid}-k{gyos.index(cur)}" data-library-gyo>{cur}</li>')
            lis.append(f'<li data-library-book data-library-text="{x["text"]}"><a href="{x["href"]}"><b>{x["name"]}</b>{freq(x["n"], r)}'
                       f'<span class="y">{x["yomi"]}</span><span class="o">{x["one"]}</span></a></li>')
        panels.append(f"""<div class="gsec" id="{gid}" data-genre-panel="{gid}" data-genre-name="{g}" data-genre-n="{len(items)}">
    <h2 class="gh">{g}<small>{len(items)}語・あいうえお順</small></h2>
    <ul class="kana" aria-label="{g}のあいうえお順">{kana}</ul>
    <ul class="glist">{''.join(lis)}</ul>
  </div>""")

    rough = S.rough_body("04b", PATH)
    svg = re.search(r'<svg width="0".*?</svg>', rough, re.S)
    tail = rough[rough.index('<section class="sec2 gara" id="tsugi">'):]
    tail, _scripts = S.split_scripts(tail)  # ラフの中のスクリプト（1問1答・しおり）は、このページでは使わない
    tail = S.link_items(tail)
    tail = tail.split("@@END@@")[0].rstrip()

    hero = f"""<section class="lst x-uhero"><div class="w">
  <div class="lst-h">
    <div>
      <a class="x-step-tag" href="/exam/#s2">勉強の道 STEP2 ことばと理論</a>
      <p class="eye">学びの移動図書館｜キャリアコンサルタント試験の用語集</p>
      <h1>キャリコンことば図鑑<span class="nw">（162語）</span></h1>
      <p class="ld">{lead}</p>
      <div class="sunline"><img src="{r}img/kata/sunny.webp" alt="サニー先生"><p class="sb"><span class="who">サニー先生</span>{bubble}</p></div>
    </div>
    <div class="art" aria-hidden="true"></div>
  </div>
</div></section>"""
    find = f"""<section class="sec2 green x-find" aria-label="言葉をさがす"><div class="w">
  <form class="zfind" role="search" onsubmit="return false" style="padding:22px 0 0"><div class="box"><input id="library-query" type="search" data-library-search autocomplete="off" aria-label="どの言葉を調べる？" placeholder="言葉をさがす（例：自己概念、傾聴、スーパー）"><button type="submit">さがす</button></div></form>
  <p class="frule">162冊のことばの本から探せます。ひらがなでも大丈夫。</p>
  <ul class="chipline" aria-label="ジャンルから探す">{chips}</ul>
  <p class="frule">印は過去6回（第27〜32回）の出題数から：3回以上 よく出る／1〜2回 ときどき出る／0回 おさえて安心（<a class="tl" href="/kakomon-keiko/">出題傾向のまとめ</a>）</p>
  <p class="frule">{trust}。{guide}</p>
</div></section>"""
    lst = f"""<section class="lst x-ichiran"><div class="w">
  {''.join(panels)}
  <p class="x-kokomade" data-kokomade hidden></p>
  <p class="x-kokomade" data-library-empty hidden>{empty}</p>
</div></section>"""
    tabs = """<script>
/* ジャンルのボタン：押した分野だけを見せる。言葉をさがしている間は、4分野ぜんぶから（js/library.js が本を出し入れする） */
(function(){var bs=[].slice.call(document.querySelectorAll('.chipline [data-genre]')),ps=[].slice.call(document.querySelectorAll('[data-genre-panel]')),
k=document.querySelector('[data-kokomade]'),q=document.querySelector('[data-library-search]');if(!bs.length||!ps.length)return;
var cur=ps[0].id;var m=(location.hash||'').match(/^#(genre-\\d)/);if(m&&document.getElementById(m[1]))cur=m[1];
function show(){var t=q&&q.value.trim();ps.forEach(function(p){
 if(t){p.hidden=!p.querySelector('[data-library-book]:not([hidden])');p.classList.add('is-q');}
 else{p.hidden=p.id!==cur;p.classList.remove('is-q');}});
 bs.forEach(function(b){b.classList.toggle('on',!t&&b.getAttribute('data-genre')===cur);b.setAttribute('aria-pressed',!t&&b.getAttribute('data-genre')===cur?'true':'false');});
 var p=document.getElementById(cur);if(k){k.hidden=!!t;k.textContent='162語のうち、ここは「'+p.getAttribute('data-genre-name')+'」の'+p.getAttribute('data-genre-n')+'語です。ほかの分野は、上のボタンで切りかえられます。';}}
bs.forEach(function(b){b.addEventListener('click',function(){cur=b.getAttribute('data-genre');if(q&&q.value){q.value='';q.dispatchEvent(new Event('input'));}show();
 var l=document.querySelector('.x-ichiran');if(l&&l.getBoundingClientRect().top<0)l.scrollIntoView({behavior:'smooth'});});});
if(q)q.addEventListener('input',function(){setTimeout(show,0);});
window.addEventListener('hashchange',function(){var m=(location.hash||'').match(/^#(genre-\\d)/);if(m){cur=m[1];show();}});
show();})();
</script>"""
    js = "\n".join([tabs,
                    f'<script src="{r}js/library.js?v=v2026.0728.1616" defer></script>',
                    f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
                    f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
                    f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>'])
    body = f"""{svg.group(0) if svg else ''}
@@TOP@@
{hero}
{find}
{lst}
{tail}
@@END@@
{js}
"""
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("ことば図鑑", None)]

    def ld_fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s","item":"https://carepicnic.com%s"}' % (
                    i + 1, n, h or P.url_of(PATH)) for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out

    out = S.page(PATH, prod, body, cat="04b", crumb=crumb, extra_css=("shiken/04b-plus.css",), ld_fix=ld_fix)
    S.check(PATH, out)
    n_books = out.count("data-library-book")
    print(f"   語の数：{n_books}（本番 {prod.count('data-library-book ')}）  リンク先がない語：",
          [x["href"] for x in data if not os.path.exists(os.path.join(ROOT, x['href'].strip('/'), 'index.html'))] or "なし")
    lost = T.lost_sentences(prod, out)
    print("   本番の文で、新しいページに見つからない文：", len(lost))
    for t in lost:
        print("     -", t[:120])


if __name__ == "__main__":
    build()
