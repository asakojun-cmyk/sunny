#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：ことば図鑑の用語ページ（162語）を、ラフ_1119 の04（ことば図鑑）の型に組みかえる道具。

- 本文（意味・たとえ・試験の説明・試験の出かた・似た言葉・1問1答・関連）は本番のページの文のまま。並びと組みだけ変える
- 授業の音声（js/lesson-player.js・scripts/make-lesson-audio.py）が読む class（term-oneliner・term-section-title・
  chara-guide__bubble・term-prose など）は、新しい組みの中にそのまま残す。読む順番も変えない。
  名前の札（モヤン・サニー先生）は CSS の data-who で出すので、読む文は1字も変わらない
- 組んだあと、音声が読む段落の「だれが・何を」が前と同じかを道具で確かめる（ちがえば書かずに止める）

使い方: python3 scripts/ippen_shiken_terms.py supervision [ほかの言葉…]   （--all で162語。いまは代表の1語だけ）
"""
import copy
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402

ROOT = P.ROOT
SUNNY = "img/kata/sunny.webp"
MOYAN = "img/parts/t/moyan_school_hat_smile-200.webp"
CLOUD = "img/parts/28_small_cloud_motif.webp"
BIO = ("3児の母。2026年に、地域連携プラットフォームの養成講習（オンライン・土曜クラス）を修了し、"
       "第33回キャリアコンサルタント試験を受けました（合格発表は2026年12月16日）。")


def inner(el):
    return "".join(str(c) for c in el.contents) if el else ""


def text(el):
    return el.get_text("", strip=True) if el else ""


def load_selector():
    import importlib.util
    spec = importlib.util.spec_from_file_location("mla", os.path.join(ROOT, "scripts/make-lesson-audio.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


MLA = load_selector()


def spoken(html, page):
    soup = BeautifulSoup(html, "html.parser")
    for w in soup.find_all("wbr"):
        w.decompose()
    return [(MLA.who(el, page), MLA.spoken_text(el, YOMI),
             "term-section-title" in (el.get("class") or []) or el.name == "h2") for el in soup.select(MLA.SELECTOR)]


import json  # noqa: E402
YOMI = json.load(open(os.path.join(ROOT, "scripts/lesson-yomi.json"), encoding="utf-8"))


def hide_part(title_html, pattern):
    """見出しの文は変えずに、見せない部分を .vh で包む（音声は前と同じ文を読む）"""
    m = re.match(pattern, title_html, re.S)
    if not m:
        return title_html
    out = []
    for i, part in enumerate(m.groups()):
        if part is None:
            continue
        out.append(part if i % 2 == 1 else (f'<span class="vh">{part}</span>' if part else ""))
    return "".join(out)


def bubble(el, who, cls=""):
    """吹き出しの <p>（中の文はそのまま）。名前は data-who で出す"""
    return f'<p class="chara-guide__bubble{(" " + cls) if cls else ""}" data-who="{who}">{inner(el)}</p>'


def build(slug):
    path = f"terms/{slug}/index.html"
    full = os.path.join(ROOT, path)
    prod = open(full, encoding="utf-8").read()
    if 'http-equiv="refresh"' in prod:
        print(f"{path}: 転送のページなのでさわらない")
        return
    soup = BeautifulSoup(prod, "html.parser")
    r = P.rel_root(path)
    art = soup.select_one("article.term-article")
    sec = {}
    order = []
    for c in art.find_all(recursive=False):
        cls = c.get("class") or []
        key = c.get("data-lesson") is not None and "lesson" or (cls[0] if cls else c.name)
        if key in ("container",):
            key = cls[-1]
        sec[key] = c
        order.append(key)

    # ---- 頭の札
    hd = sec["term-header"]
    num = re.search(r"TERM\s*(\d+)", text(hd.select_one(".term-header__number")))
    no = int(num.group(1)) if num else None
    kako = hd.select_one(".kako-badge b")
    times = int(kako.get_text()) if kako else None
    name = inner(hd.select_one(".term-header__name"))
    name_t = text(hd.select_one(".term-header__name"))
    yomi = inner(hd.select_one(".term-header__reading"))
    cat_el = hd.select_one(".term-header__category")
    for sp in cat_el.select("span[aria-hidden]"):
        sp.decompose()
    category = text(cat_el)
    upd = text(hd.select_one(".updated-date")).replace("更新日:", "").strip()
    one = sec["term-oneliner"]
    bubbles = one.select(".chara-guide__bubble")
    moyan_q, sunny_a = bubbles[0], bubbles[-1]
    if times is None:
        tag = ""
    elif times >= 3:
        tag = f'<li class="hi">{"".join(f"<img src=\"{r}{CLOUD}\" alt=\"\">" for _ in range(3))}よく出る・過去6回で <span class="num">{times}</span> 回</li>'
    elif times >= 1:
        tag = f'<li>{"".join(f"<img src=\"{r}{CLOUD}\" alt=\"\">" for _ in range(2))}ときどき出る・過去6回で <span class="num">{times}</span> 回</li>'
    else:
        tag = f'<li><img src="{r}{CLOUD}" alt="">おさえて安心・過去6回で <span class="num">0</span> 回</li>'
    ans = BeautifulSoup(inner(sunny_a), "html.parser")
    for s in ans.find_all("strong"):
        s.name = "span"
        s["class"] = "mark"
    lesson = sec.get("lesson")
    mount = str(lesson) if lesson is not None else ""
    listen = ""
    if lesson is not None:
        listen = ('<button type="button" class="x-listen-b" data-lesson-go hidden><span class="ic"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 9.5a5 5 0 0 1 10 0c0 2.6-1.6 3.6-2.6 4.6-.9.9-1 1.9-1.4 3.2A2.6 2.6 0 0 1 8.5 18"/><path d="M10 10a2 2 0 0 1 4 0c0 1-.7 1.4-1.2 1.9"/></svg></span><span class="lb">授業をきく</span></button>')
    hint = '<span data-lesson-hint hidden>耳のボタンで、モヤンとサニー先生の授業が聞けるよ／</span>' if lesson is not None else ""
    hero = f"""<section class="zhead x-uhero"><div class="w">
  <div class="zh">
    <div class="zh-l">
      <a class="x-step-tag" href="/exam/#s2">勉強の道 STEP2 ことばと理論</a>
      <div class="zh-card">
        <p class="zh-no">{f'<span class="no">No.{no}</span>' if no else ''}<span class="gen">{category}</span></p>
        <h1>{name}</h1>
        <p class="yomi">{yomi}</p>
        <div class="zh-ans"><img src="{r}{SUNNY}" alt="サニー先生"><p><span class="who">ひとことでいうと</span>{ans}</p></div>
        {f'<ul class="zh-tags">{tag}</ul>' if tag else ''}
        <p class="frule">印は過去6回（第27〜32回）の出題数から：3回以上 よく出る／1〜2回 ときどき出る／0回 おさえて安心</p>
      </div>
    </div>
    <div class="zh-side">
      <div class="x-row">
        <form class="zfind" role="search" action="/search/" method="get"><div class="box"><input type="search" name="q" aria-label="ほかの言葉をさがす" placeholder="ほかの言葉をさがす（例：ラポール）"><button type="submit" aria-label="さがす"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg></button></div></form>
        {listen}
      </div>
      <p class="x-row-t">{hint}<a class="tl" href="/terms/">162語の一覧</a></p>
    </div>
  </div>
</div><i class="oka" aria-hidden="true"></i></section>"""

    # ---- 答え（ひとことでいうと）
    t1 = one.select_one(".term-section-title")
    t1_html = hide_part(inner(t1), r"^()(.*?とは？)(\s*ひとことでいうと)$")
    kotae = f"""<section class="sec2 green term-oneliner" id="kotae"><div class="w nar">
  <p class="eye c">ひとことでいうと</p>
  <h2 class="c term-section-title">{t1_html}</h2>
  <div class="pair" style="margin:14px 0 0"><div class="pm chara-guide--moyan">{bubble(moyan_q, "モヤン")}<img src="{r}{MOYAN}" alt="モヤン"></div></div>
  <div class="sun2 rise chara-guide--sunny"><img src="{r}{SUNNY}" alt="サニー先生">{bubble(sunny_a, "サニー先生", "sb")}</div>
  {mount}
</div></section>"""

    # ---- 意味（ざっくり・たとえ・子育て → 試験の説明）
    lad = []
    for k in ("term-kids", "term-analogy", "term-life"):
        s = sec.get(k)
        if s is None:
            continue
        lad.append(f'<div class="lr {k}"{(" id=\"" + s["id"] + "\"") if s.get("id") else ""}><p class="lt term-section-title">{inner(s.select_one(".term-section-title"))}</p>'
                   f'<div class="term-prose">{inner(s.select_one(".term-prose"))}</div></div>')
    formal = sec.get("term-formal")
    rs_sheet = ""
    seishiki = ""
    if formal is not None:
        box = formal.select_one(".term-formal__box")
        card = box.select_one(".rs-card") if box else None
        if card:
            card.decompose()
        sh = formal.select_one(".rs-sheet")
        if sh:
            rs_sheet = str(sh.extract())
        ft = formal.select_one(".term-section-title")
        ft_html = inner(ft)
        m = re.match(r"^(.*?の意味)\((.*)\)$", ft_html, re.S)
        if m:  # 「〇〇の意味(試験で必要な正式な説明)」→ 見せるのは「試験で必要な正式な説明」だけ（読む文は同じ）
            ft_html = f'<span class="vh">{m.group(1)}(</span>{m.group(2)}<span class="vh">)</span>'
        seishiki = (f'<p class="down">試験の言葉で</p>\n<div class="seishiki term-formal" id="sec-formal"><p class="lb term-section-title">{ft_html}</p>'
                    f'{str(box) if box else ""}'
                    + "".join(str(x) for x in formal.find_all(recursive=False) if x is not ft and x is not box) + "</div>")
    extra_imi = "".join(str(sec[k]) for k in order if k in ("term-diagram-section", "law-notice", "term-deepdive"))
    imi = f"""<section class="zs" id="imi">
      <p class="eye">意味</p>
      <h2>{name_t}の意味</h2>
      <div class="ladder">{''.join(lad)}</div>
      {seishiki}
      {extra_imi}
    </section>"""

    # ---- 試験の出かた
    adv = sec.get("term-exam-advice")
    quiz = sec.get("term-quiz")
    saimoku = quiz.select_one(".quiz-saimoku") if quiz is not None else None
    hani = ""
    if saimoku is not None:
        a = saimoku.select_one("a")
        a_href = a["href"] if a else ""
        b = saimoku.select_one("b")
        if b:
            b.decompose()
        if a:
            a.decompose()
        hani = (f'<div class="hani"><span class="k">出題範囲（細目）</span><span>{inner(saimoku).strip()}</span>'
                + (f'<a class="tl" href="{a_href}">細目との対応表</a>' if a_href else "") + "</div>")
        saimoku.decompose()
    shiken_parts = []
    if adv is not None:
        at = adv.select_one(".term-section-title")
        mq = adv.select_one(".chara-guide--moyan .chara-guide__bubble")
        lst = adv.select_one(".exam-advice__list")
        shiken_parts.append(f"""<h2>{inner(at)}</h2>
      <div class="pair">
        {f'<div class="pm chara-guide--moyan">{bubble(mq, "モヤン")}<img src="{r}{MOYAN}" alt="モヤン"></div>' if mq else ''}
        <div class="ps exam-advice"><img src="{r}{SUNNY}" alt="サニー先生"><div class="adv"><p class="who2">サニー先生の試験アドバイス</p>{str(lst) if lst else ''}</div></div>
      </div>""")
    for k in order:
        if k in ("term-oboekata", "term-pitfall", "kw-talk", "tool-try", "term-exam-points", "term-try", "term-episode"):
            shiken_parts.append(f'<div class="zx">{sec[k]}</div>')
    shiken = ""
    if shiken_parts or hani:
        cls = "zs term-exam-advice" if adv is not None else "zs"
        shiken = f"""<section class="{cls}" id="shiken">
      <p class="eye">試験の出かた</p>
      {''.join(shiken_parts) if adv is not None else f'<h2>{name_t}は試験でこう出る</h2>' + ''.join(shiken_parts)}
      {hani}
    </section>"""
        if adv is not None:
            # 音声が読むのは .term-exam-advice の中の吹き出しとリストだけ。ほかの段（覚え方など）は別の section に分ける
            others = "".join(p for p in shiken_parts[1:])
            shiken = f"""<section class="zs term-exam-advice" id="shiken">
      <p class="eye">試験の出かた</p>
      {shiken_parts[0]}
      {hani}
    </section>""" + (f'\n<section class="zs zs-sub">{others}</section>' if others else "")

    # ---- 似た言葉
    sim = sec.get("term-similar")
    chigai = ""
    if sim is not None:
        st = sim.select_one(".term-section-title")
        dl = sim.select_one("dl")
        for d in dl.find_all("div", recursive=False):
            d["class"] = "cc"
        chigai = f"""<section class="zs term-similar" id="chigai">
      <p class="eye">似た言葉</p>
      <h2 class="term-section-title">{inner(st)}</h2>
      <div class="cmp"><div class="cc me"><p class="cn"><small>この言葉</small>{name}</p><p class="d">{inner(sunny_a)}</p></div>{str(dl).replace('<dl>', '<dl class="cmp-dl">', 1)}</div>
    </section>"""

    # ---- 1問1答
    quiz_html = ""
    if quiz is not None:
        qt = quiz.select_one(".term-section-title")
        boxes = "".join(str(b) for b in quiz.find_all(recursive=False) if b is not qt)
        past = sec.get("past-questions")
        links = ""
        if past is not None:
            links = "・".join(inner(li) for li in past.select(".past-questions__links li"))
        quiz_html = f"""<section class="zs" id="quiz">
      <p class="eye">1問1答</p>
      <h2>{inner(qt).replace("(当サイトオリジナル)", "")}</h2>
      <div class="qz-steps" data-qz-steps><p class="qz-flow">えらぶ → 答えと解説 → 次の問題へ</p>{boxes}</div>
      {f'<p class="note2" style="margin-top:12px">過去問は、公式サイトで：{links}（学科試験は両機関共通）</p>' if links else ''}
    </section>"""

    # ---- 関連
    kan = []
    th = sec.get("term-theorists")
    if th is not None:
        kan.append(f'<div class="zx">{th}</div>')
    rel = sec.get("related")
    if rel is not None:
        items = []
        for li in rel.select(".related__list li"):
            a = li.select_one("a")
            if not a:
                continue
            items.append(f'<li><a href="{a["href"]}"><span class="k">{inner(a.select_one(".related__type"))}</span>'
                         f'<b>{inner(a.select_one(".related__item-title"))}</b><small>{inner(a.select_one(".related__desc"))}</small>'
                         f'<span class="more">もっと詳しく →</span></a></li>')
        kan.append(f'<ul class="rel">{"".join(items)}</ul>')
    nx = sec.get("term-next")
    if nx is not None:
        a = nx.select_one("a")
        kan.append(f'<div class="pn one"><a class="nx" href="{a["href"]}"><small>つぎに読むなら →</small>{inner(a.select_one("b"))}</a></div>')
    sh = sec.get("term-share")
    if sh is not None:
        kan.append('<p class="share">勉強仲間に送る：' + "".join(
            f'<a href="{a["href"]}" rel="noopener" target="_blank">{text(a)}</a>' for a in sh.select("a")) + "</p>")
    bs = sec.get("book-shelf")
    if bs is not None:
        kan.append(f'<div class="zx">{bs}</div>')
    refs = sec.get("term-refs")
    if refs is not None:
        lis = "".join(f"<li>{inner(li)}</li>" for li in refs.select(".term-refs__list li"))
        note = refs.select_one(".term-refs__note")
        first = text(refs.select_one(".term-refs__list li"))
        kan.append(f"""<details class="fold"><summary>書いた人：キャリコン学びピクニック運営者／参考：{first.split('(')[0].split('（')[0]}ほか／更新日 {upd}</summary><div class="in">
        <p style="margin:6px 0">{BIO}</p>
        <ul class="srcl">{lis}</ul>{f'<p style="margin:6px 0">{inner(note)}</p>' if note else ''}<p style="margin:6px 0"><a href="/about/">このサイトについて</a></p>
      </div></details>""")
    kanren = f"""<section class="zs" id="kanren">
      <p class="eye">関連の言葉</p>
      <h2>関連用語・関連する理論家</h2>
      {''.join(kan)}
    </section>"""

    # ---- しおり・赤シート
    toc = [(i, t) for i, t, ok in (("imi", "意味", True), ("shiken", "試験の出かた", bool(shiken)), ("chigai", "似た言葉", bool(chigai)),
                                     ("quiz", "1問1答", bool(quiz_html)), ("kanren", "関連の言葉", True)) if ok]
    rs = ""
    if rs_sheet:
        rs = f"""<div class="rs"><p class="rs-h"><img src="{r}{SUNNY}" alt=""><span><span class="x-free">無料・登録なし</span>赤シートで覚える1枚 A4・PDF</span></p><p>このページの「試験で出るところ」を、noteの直前対策テキストと同じ形で1枚にまとめました。</p><button type="button" class="go" data-rs-print>PDFで保存・印刷する</button>
  <a class="tx" href="/text/"><img src="{r}img/text-cover-s.webp" alt="直前対策テキストの表紙"><span>全部まとめて使うなら<br>直前対策テキスト</span></a></div>"""
    rail = f"""<aside class="rail">
    <nav class="shiori" aria-label="このページの中"><p class="st">このページの中</p><ol>{''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)}</ol></nav>
    <div class="rail-x">{rs}<p class="back"><a class="tl" href="/terms/">ことば図鑑の一覧へ</a></p></div>
  </aside>"""

    # ---- ラフの下の段（次の一歩・出口・ピクニック・一番下の帯）はラフのまま
    rough = S.rough_body("04", path)
    tail = rough[rough.index('<section class="sec2 gara" id="tsugi">'):]
    tail, scripts = S.split_scripts(tail)
    tail = S.link_items(tail)

    svg = re.search(r'<svg width="0".*?</svg>', rough, re.S).group(0)
    body = f"""{svg}
@@TOP@@
@@MAIN@@
{hero}

{kotae}

<div class="zbody"><div class="w zgrid">
  {rail}
  <div class="zmain">
    {imi}
    {shiken}
    {chigai}
    {quiz_html}
    {kanren}
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

    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("ことば図鑑", "/terms/"), (name_t, None)]

    def ld_fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s","item":"https://carepicnic.com%s"}' % (
                    i + 1, n, h or P.url_of(path)) for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out

    # 音声が読む段落を、書く前にくらべる
    before = spoken(prod, path.rsplit("/", 1)[0])
    S_out = S.page(path, prod, body, cat="04", crumb=crumb, extra_css=("lesson-player.css", "red-sheet.css"), ld_fix=ld_fix)
    after = spoken(S_out, path.rsplit("/", 1)[0])
    if before != after:
        open(full, "w", encoding="utf-8").write(prod)
        print(f"{path}: 音声が読む段落が変わるので、書かずにもとに戻した（前{len(before)}・後{len(after)}）")
        for i, (a, b) in enumerate(zip(before, after)):
            if a != b:
                print("   ", i, a, "→", b)
                break
        return False
    S.check(path, S_out)
    print(f"   音声が読む段落：{len(after)}（前と同じ）")
    return True


if __name__ == "__main__":
    S.prepare()
    for s in sys.argv[1:]:
        build(s)
