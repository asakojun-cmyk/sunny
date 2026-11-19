#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：理論家図鑑の人物ページ（66人）を、ラフ_1119 の05（理論家図鑑）の型に組みかえる道具。

- 本文（ピクニックのあいさつ・ひとこと・ざっくり・たとえ・キーワード・試験のポイント・混同しやすい理論家・
  エピソード・1問1答・関連）は本番の文のまま。並びと組みだけ変える
- 授業の音声が読む class（picnic-intro__line・term-oneliner・term-section-title・term-prose・term-formal dl>div・
  mini-say・term-exam-points・chara-guide__bubble・term-episode など）と、読む人を決める親の class は、そのまま残す。
  読む順番も変えない。書く前に「だれが・何を」を前とくらべ、ちがえば書かない
- 似顔絵は img/nigaoe/<slug>.webp（丸の中はあお：alt を「〜の似顔絵」にすると kata-shiken.css が色をつける）
- 前の人・次の人は、本番の「THEORIST 番号」の順

使い方: python3 scripts/ippen_shiken_theorists.py rogers [ほかの人…]
"""
import glob
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402
from ippen_shiken_terms import inner, text, spoken, bubble, BIO, SUNNY, MOYAN, CLOUD  # noqa: E402

ROOT = P.ROOT


def roster():
    """本番の66人：番号 → (slug, 名前)"""
    out = {}
    for f in glob.glob(os.path.join(ROOT, "theorists/*/index.html")):
        s = open(f, encoding="utf-8").read()
        m = re.search(r"THEORIST\s*(\d+)", s)
        n = re.search(r'<h1 class="term-header__name">(.*?)</h1>', s, re.S)
        if m and n:
            out[int(m.group(1))] = (f.split("/")[-2], re.sub(r"<[^>]+>", "", n.group(1)).strip())
    return out


def face(slug, name, cls):
    return (f'<span class="nf {cls}"><img src="{{r}}img/nigaoe/{slug}.webp" alt="{name}の似顔絵" loading="lazy"></span>'
            if os.path.exists(os.path.join(ROOT, f"img/nigaoe/{slug}.webp"))
            else f'<span class="nf {cls} ini" aria-hidden="true">{name[:1]}</span>')


def build(slug):
    path = f"theorists/{slug}/index.html"
    full = os.path.join(ROOT, path)
    prod = S.prod_html(path)  # 組みかえる前の版（git）から読む。何度回しても同じ
    soup = BeautifulSoup(prod, "html.parser")
    r = P.rel_root(path)
    art = soup.select_one("article.theorist-article")
    kids = [c for c in art.find_all(recursive=False)]

    def cls0(c):
        if c.get("data-lesson") is not None:
            return "lesson"
        return (c.get("class") or [c.name])[0]

    first = {}
    for c in kids:
        first.setdefault(cls0(c), c)

    # ---- 人物カード
    hd = first["term-header"]
    num = re.search(r"THEORIST\s*(\d+)", text(hd.select_one(".term-header__number")))
    no = int(num.group(1)) if num else None
    kako = hd.select_one(".kako-badge b")
    times = int(kako.get_text()) if kako else None
    name = inner(hd.select_one(".term-header__name"))
    name_t = text(hd.select_one(".term-header__name"))
    en = inner(hd.select_one(".term-header__reading"))
    cat = text(hd.select_one(".term-header__category"))
    cat = re.sub(r"^[^\w（(「]+", "", cat).strip()
    upd = text(hd.select_one(".updated-date")).replace("更新日:", "").strip()
    era = first.get("theorist-era")
    facts, era_html = "", ""
    if era is not None:
        y = era.select_one(".theorist-era__years")
        facts = text(y)
        t = era.select_one(".theorist-era__text")
        inf = era.select_one(".theorist-era__influence")
        if inf is not None and inf.b:
            inf.b.name = "span"
            inf.span["class"] = "k"
        era_html = (f'<div class="era">{f"<p>{inner(t)}</p>" if t else ""}'
                    f'{f"<p style=\"margin:0\">{inner(inf)}</p>" if inf else ""}</div>')
    one = first["term-oneliner"]
    one_p = one.select_one(".term-prose p")
    ans = BeautifulSoup(inner(one_p), "html.parser")
    if times is None:
        tag = ""
    elif times >= 3:
        tag = f'<li class="hi">{"".join(f"<img src=\"{r}{CLOUD}\" alt=\"\">" for _ in range(3))}よく出る・過去6回で <span class="num">{times}</span> 回</li>'
    elif times >= 1:
        tag = f'<li>{"".join(f"<img src=\"{r}{CLOUD}\" alt=\"\">" for _ in range(2))}ときどき出る・過去6回で <span class="num">{times}</span> 回</li>'
    else:
        tag = f'<li><img src="{r}{CLOUD}" alt="">おさえて安心・過去6回で <span class="num">0</span> 回</li>'
    lesson = first.get("lesson")
    listen = hint = ""
    if lesson is not None:
        listen = ('<button type="button" class="x-listen-b" data-lesson-go hidden><span class="ic"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 9.5a5 5 0 0 1 10 0c0 2.6-1.6 3.6-2.6 4.6-.9.9-1 1.9-1.4 3.2A2.6 2.6 0 0 1 8.5 18"/><path d="M10 10a2 2 0 0 1 4 0c0 1-.7 1.4-1.2 1.9"/></svg></span><span class="lb">授業をきく</span></button>')
        hint = '<span data-lesson-hint hidden>耳のボタンで、モヤンとサニー先生の授業が聞けるよ／</span>'
    hero = f"""<section class="zhead x-uhero"><div class="w">
  <div class="zh"><div class="zh-l">
    <a class="x-step-tag" href="/exam/#s2">勉強の道 STEP2 ことばと理論</a>
    <div class="zh-card" id="jinbutsu">
      <div class="pc">
        <div class="pc-face">{face(slug, name_t, "nf-hero").replace("{r}", r)}</div>
        <div>
          <p class="zh-no">{f'<span class="no">No.{no:02d}</span>' if no else ''}<span class="gen">{cat}</span></p>
          <h1>{name}</h1>
          <p class="pc-en">{en}</p>
          {f'<p class="pc-facts">{facts}</p>' if facts else ''}
        </div>
      </div>
      <div class="hito1"><img src="{r}{SUNNY}" alt="サニー先生"><p><span class="who">ひとことでいうと</span>{ans}</p></div>
      {era_html}
      {f'<ul class="zh-tags">{tag}</ul>' if tag else ''}
      <p class="frule">印は過去6回（第27〜32回）の出題数から：3回以上 よく出る／1〜2回 ときどき出る／0回 おさえて安心</p>
    </div>
    <div class="x-row">
      <form class="zfind" role="search" action="/search/" method="get"><div class="box"><input type="search" name="q" aria-label="ほかの理論家をさがす" placeholder="ほかの理論家をさがす（例：スーパー）"><button type="submit" aria-label="さがす"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg></button></div></form>
      {listen}
    </div>
    <p class="x-row-t">{hint}<a class="tl" href="/theorists/">66人の一覧と系譜</a></p>
  </div></div>
</div><i class="oka" aria-hidden="true"></i></section>"""

    # ---- 本番の段を、順番どおり4つの段（芯・キーワード・試験・もっと）に分ける
    zone = "shin"
    zones = {"shin": [], "kw": [], "shiken": [], "more": []}
    rs_sheet = ""
    skip = {"term-header", "theorist-era", "lesson", "term-header__portrait-note", "study-back", "pre-enroll", "author-profile"}
    for c in kids:
        k = cls0(c)
        if k in skip:
            continue
        if k == "term-formal":
            zone = "kw"
        elif k in ("term-exam-points", "term-exam-advice", "term-similar", "term-try") and zone in ("shin", "kw"):
            zone = "shiken"
        elif k in ("term-quiz", "past-questions", "term-episode", "term-more", "related", "book-shelf"):
            zone = "more"
        zones[zone].append((k, c))

    def picnic_intro(c):
        lines = []
        for ln in c.select(".picnic-intro__line"):
            cl = " ".join(ln.get("class"))
            p = ln.select_one("p")
            guest = "picnic-intro__line--guest" in cl
            img = "" if guest else f'<img src="{r}{SUNNY}" alt="サニー先生">'
            gimg = face(slug, name_t, "nf-pn").replace("{r}", r) if guest else ""
            lines.append(f'<div class="{cl} pi">{img}{gimg}<p>{inner(p)}</p></div>')
        return f'<div class="picnic-intro pis">{"".join(lines)}</div>'

    def ladder_item(k, c):
        t = c.select_one(".term-section-title")
        return (f'<div class="lr {k}"><p class="lt term-section-title">{inner(t)}</p>'
                f'<div class="term-prose">{inner(c.select_one(".term-prose"))}</div></div>')

    def kwtalk(c):
        out = []
        for ms in c.select(".mini-say"):
            cl = " ".join(ms.get("class"))
            p = ms.select_one(".mini-say__bubble")
            if "mini-say--moyan" in cl:
                out.append(f'<div class="pm {cl}"><p class="mini-say__bubble">{inner(p)}</p><img src="{r}{MOYAN}" alt="モヤン"></div>')
            else:
                out.append(f'<div class="ps {cl}"><img src="{r}{SUNNY}" alt="サニー先生"><p class="mini-say__bubble">{inner(p)}</p></div>')
        return f'<div class="pair kw-talk">{"".join(out)}</div>'

    # 芯
    shin = []
    lad = []
    for k, c in zones["shin"]:
        if k == "picnic-intro":
            shin.append(picnic_intro(c))
        elif k == "term-oneliner":
            t = c.select_one(".term-section-title")
            shin.append(f'<div class="term-oneliner one2"><p class="lt2 term-section-title">{inner(t)}</p>'
                        f'<div class="sun2 chara-guide--sunny"><img src="{r}{SUNNY}" alt="サニー先生"><div class="sb term-prose">{inner(c.select_one(".term-prose"))}</div></div></div>')
        elif k in ("term-kids", "term-analogy", "term-life"):
            lad.append(ladder_item(k, c))
        else:
            if lad:
                shin.append(f'<div class="ladder">{"".join(lad)}</div>')
                lad = []
            shin.append(f'<div class="zx">{c}</div>')
    if lad:
        shin.append(f'<div class="ladder">{"".join(lad)}</div>')
    mount = str(lesson) if lesson is not None else ""
    sec_shin = f"""<section class="zs" id="shin">
      <p class="eye">理論の芯</p>
      <h2>{name_t}の考えを、ざっくり</h2>
      {mount}
      {''.join(shin)}
    </section>"""

    # キーワード
    kw = []
    kw_title = ""
    for k, c in zones["kw"]:
        if k == "term-formal":
            card = c.select_one(".rs-card")
            if card:
                card.decompose()
            sh = c.select_one(".rs-sheet")
            if sh:
                rs_sheet += str(sh.extract())
            t = c.select_one(".term-section-title")
            box = c.select_one(".term-formal__box")
            if not kw_title:
                kw_title = inner(t)
                rest = "".join(str(x) for x in c.find_all(recursive=False) if x is not t)
                kw.append(f'<div class="{" ".join(c.get("class"))} kwbox"><h2 class="term-section-title">{inner(t)}</h2>{rest}</div>')
            else:
                kw.append(f'<div class="{" ".join(c.get("class"))} kwbox zx2">{"".join(str(x) for x in c.find_all(recursive=False))}</div>')
        elif k == "kw-talk":
            kw.append(kwtalk(c))
        else:
            kw.append(f'<div class="zx">{c}</div>')
    sec_kw = f"""<section class="zs" id="kw">
      <p class="eye">キーワード</p>
      {''.join(kw)}
    </section>"""

    # 試験の出かた
    sh_parts = []
    for k, c in zones["shiken"]:
        if k == "term-exam-points":
            t = c.select_one(".term-section-title")
            ul = c.select_one("ul")
            ul["class"] = (ul.get("class") or []) + ["chk3"]
            sh_parts.append(f'<div class="term-exam-points"><h2 class="term-section-title">{inner(t)}</h2>{ul}</div>')
        elif k == "term-exam-advice":
            at = c.select_one(".term-section-title")
            mq = c.select_one(".chara-guide--moyan .chara-guide__bubble")
            lst = c.select_one(".exam-advice__list")
            sh_parts.append(f"""<div class="term-exam-advice"><h3 class="h3s">{inner(at)}</h3><div class="pair">
        {f'<div class="pm chara-guide--moyan">{bubble(mq, "モヤン")}<img src="{r}{MOYAN}" alt="モヤン"></div>' if mq else ''}
        <div class="ps exam-advice"><img src="{r}{SUNNY}" alt="サニー先生"><div class="adv"><p class="who2">サニー先生の試験アドバイス</p>{lst if lst else ''}</div></div>
      </div></div>""")
        elif k == "term-similar":
            st = c.select_one(".term-section-title")
            dl = c.select_one("dl")
            for d in dl.find_all("div", recursive=False):
                d["class"] = "cc"
            notes = "".join(f'<p class="note2">{inner(n)}</p>' for n in c.select(".term-section-note"))
            sh_parts.append(f"""<div class="term-similar"><h3 class="h3s term-section-title">{inner(st)}</h3>
      <div class="cmp"><div class="cc me"><p class="cn"><small>この人</small>{name}</p><p class="d">{inner(one_p)}</p></div>{str(dl).replace('<dl>', '<dl class="cmp-dl">', 1)}</div>{notes}</div>""")
        elif k == "kw-talk":
            sh_parts.append(kwtalk(c))
        else:
            sh_parts.append(f'<div class="zx">{c}</div>')
    sec_shiken = f"""<section class="zs" id="shiken">
      <p class="eye">試験の出かた</p>
      {''.join(sh_parts)}
    </section>""" if sh_parts else ""

    # もっと（1問1答・エピソード・写真と動画・関連）— 押すと開く
    quiz = past = epi = more = rel = shelf = None
    extra_more = []
    for k, c in zones["more"]:
        if k == "term-quiz":
            quiz = c
        elif k == "past-questions":
            past = c
        elif k == "term-episode":
            epi = c
        elif k == "term-more":
            more = c
        elif k == "related":
            rel = c
        elif k == "book-shelf":
            shelf = c
        else:
            extra_more.append(f'<div class="zx">{c}</div>')
    dets = []
    if quiz is not None:
        qt = quiz.select_one(".term-section-title")
        boxes = [b for b in quiz.find_all(recursive=False) if b is not qt]
        n = len([b for b in boxes if b.get("data-quiz") is not None])
        links = "・".join(inner(li) for li in past.select(".past-questions__links li")) if past is not None else ""
        dets.append(f"""<details open id="quiz"><summary>1問1答で確かめる<small>{n}問・当サイトオリジナル</small></summary><div class="in">
          <div class="qz-steps" data-qz-steps><p class="qz-flow">えらぶ → 答えと解説 → 次の問題へ</p>{''.join(str(b) for b in boxes)}</div>
          {f'<p class="note2" style="margin-top:12px">過去問は、公式サイトで：{links}（学科試験は両機関共通）</p>' if links else ''}
        </div></details>""")
    if epi is not None or more is not None:
        body_e = ""
        if epi is not None:
            et = epi.select_one(".term-section-title")
            rest = "".join(str(x) for x in epi.find_all(recursive=False) if x is not et)
            body_e += f'<div class="term-episode" id="episode"><p class="vh term-section-title">{inner(et)}</p>{rest}</div>'
        if os.path.exists(os.path.join(ROOT, f"obento/{slug}/index.html")):
            body_e += f'<p><a class="tl" href="/obento/{slug}/">{name_t}さんとのお弁当のお話を読む</a></p>'
        if more is not None:
            ls = "・".join(f'<a href="{a["href"]}" rel="noopener nofollow" target="_blank">{text(a)}</a>' for a in more.select(".more-links a"))
            body_e += f'<p class="note2">写真・くわしい経歴・解説動画は、外部サイトで：{ls}</p>'
        pn_note = first.get("term-header__portrait-note")
        if pn_note is not None:
            body_e += f'<p class="note2">{inner(pn_note)}</p>'
        summ = text(epi.select_one(".term-section-title")) if epi is not None else "もっと知る（写真・動画）"
        dets.append(f'<details open><summary>{summ}<small>人となりを知ると、ぐっと記憶に残ります</small></summary><div class="in">{body_e}</div></details>')
    if rel is not None:
        items = []
        for li in rel.select(".related__list li"):
            a = li.select_one("a")
            if not a:
                continue
            items.append(f'<li><a href="{a["href"]}"><span class="k">{inner(a.select_one(".related__type"))}</span>'
                         f'<b>{inner(a.select_one(".related__item-title"))}</b><small>{inner(a.select_one(".related__desc"))}</small>'
                         f'<span class="more">もっと詳しく →</span></a></li>')
        names = "・".join(text(li.select_one(".related__item-title")) for li in rel.select(".related__list li") if li.select_one(".related__item-title"))
        dets.append(f'<details><summary>{text(rel.select_one(".related__title"))}<small>{names}</small></summary><div class="in"><ul class="rel">{"".join(items)}</ul></div></details>')
    if shelf is not None:
        dets.append(f'<details><summary>さらに学べる本<small>本棚から</small></summary><div class="in"><div class="zx">{shelf}</div></div></details>')
    ros = roster()
    nav = ""
    if no in ros:
        pv, nx = ros.get(no - 1), ros.get(no + 1)
        a1 = (f'<a class="pnf" href="/theorists/{pv[0]}/">{face(pv[0], pv[1], "nf-pn").replace("{r}", r)}<span><small>← 前の人（No.{no-1:02d}）</small>{pv[1]}</span></a>' if pv else "<span></span>")
        a2 = (f'<a class="nx pnf" href="/theorists/{nx[0]}/"><span><small>次の人（No.{no+1:02d}） →</small>{nx[1]}</span>{face(nx[0], nx[1], "nf-pn").replace("{r}", r)}</a>' if nx else "")
        nav = f'<div class="pn">{a1}{a2}</div>'
    sec_more = f"""<section class="zs" id="motto">
      <p class="eye">もっと</p>
      <h2>確かめる・覚える・つなげる</h2>
      {''.join(extra_more)}
      <div class="more2"><p class="mh">押すと開きます</p>{''.join(dets)}</div>
      <p style="margin-top:18px"><a class="tl" href="/theorists/keifu/">理論家の系譜をぜんぶ見る</a></p>
      {nav}
      <details class="fold"><summary>書いた人：キャリコン学びピクニック運営者／更新日 {upd}</summary><div class="in"><p style="margin:6px 0">{BIO}</p><p style="margin:6px 0"><a href="/about/">このサイトについて</a></p></div></details>
    </section>"""

    toc = [("shin", "理論の芯"), ("kw", "キーワード")] + ([("shiken", "試験の出かた")] if sec_shiken else []) + [("motto", "1問1答・エピソード")]
    rs = ""
    if rs_sheet:
        rs = f"""<div class="rs"><p class="rs-h"><img src="{r}{SUNNY}" alt=""><span><span class="x-free">無料・登録なし</span>赤シートで覚える1枚 A4・PDF</span></p><p>このページの「試験で出るところ」を、noteの直前対策テキストと同じ形で1枚にまとめました。</p><button type="button" class="go" data-rs-print>PDFで保存・印刷する</button>
  <a class="tx" href="/text/"><img src="{r}img/text-cover-s.webp" alt="直前対策テキストの表紙"><span>全部まとめて使うなら<br>直前対策テキスト</span></a></div>"""
    rail = f"""<aside class="rail">
    <nav class="shiori" aria-label="このページの中"><p class="st">このページの中</p><ol>{''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)}</ol></nav>
    <div class="rail-x">{rs}<p class="back"><a class="tl" href="/theorists/">理論家図鑑の一覧へ</a></p></div>
  </aside>"""

    rough = S.rough_body("05", path)
    tail = rough[rough.index('<section class="sec2 gara" id="tsugi">'):]
    tail, _scripts = S.split_scripts(tail)
    tail = S.link_items(tail)
    svg = re.search(r'<svg width="0".*?</svg>', S.rough_body("04", path), re.S)
    body = f"""{svg.group(0) if svg else ''}
@@TOP@@
@@MAIN@@
{hero}

<div class="zbody"><div class="w zgrid">
  {rail}
  <div class="zmain">
    {sec_shin}
    {sec_kw}
    {sec_shiken}
    {sec_more}
    {rs_sheet}
  </div>
</div></div>
{tail.split('@@END@@')[0].rstrip()}
@@/MAIN@@
@@END@@
"""
    js = [f'<script src="{r}js/red-sheet.js?v=2026.1028" defer></script>',
          f'<script src="{r}js/quiz.js?v=2026.1018q" defer></script>',
          f'<script src="{r}js/lesson-player.js?v=2026.1120" defer></script>',
          f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
          f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
          f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>']
    body = body.replace("@@END@@\n", "@@END@@\n" + "\n".join(js) + "\n")
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("理論家図鑑", "/theorists/"), (name_t, None)]

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
    out = S.page(path, prod, body, cat="05", crumb=crumb,
                 extra_css=("lesson-player.css", "red-sheet.css", "shiken/05-plus.css"), ld_fix=ld_fix)
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
