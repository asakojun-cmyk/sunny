#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：/school-guides/ の10ページを、ラフ03の型（新しい型の記事）に組みかえる道具。

- 本文は変えない。いまの本文の節（guide-section）を、そのまま「くわしく N」の段（sec2 hb）に流しこむ
- 新しく書くのは3か所だけ：頭の段の悩み（qb）・答えの1行（サニー先生の吹き出し）・目次の1行（いまの目次の小さい行を使う）
- 吹き出し（mini-say）は新しい型の吹き出しに（サニー先生とちゃんは左・モヤンは右・ちゃんの「体験」の札は残す）
- よくある質問（gk-qa）は新しい型の .faq に。あわせて読みたい → 次の一歩のカード。書いた人 → .kakite
- 計算・診断のしかけ（kyufu-check・kyufu-calc・guide-check・shindan など）は HTML と js をそのまま。
  見た目は css/guide-kata.css（guide-kit.css と、古い CSS からその部品の分だけを .gk の中に限って写したもの・この道具が作る）
- 頭（計測・title・説明文・canonical・構造化データ）は本番のまま。ヘッダー・フッターなどは共通の部品（ippen_parts）
- 書きかえる前のページは、控え（--moto のフォルダ）から読む。控えがなければ、いまのページを控えてから使う

使い方: ~/voicevox-engine/venv/bin/python scripts/ippen_build_guides.py [--moto 控えのフォルダ] [名前 ...]
"""
import copy
import difflib
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup, NavigableString

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_from_rough as F  # noqa: E402
import ippen_yomiyasu as Y  # noqa: E402

ROOT = P.ROOT
CSS = os.path.join(ROOT, "css")
MOTO = "/private/tmp/claude-501/-Users-iwawakiasako/b0ab8e18-46b0-4dd4-a73e-3ba79d54a7bf/scratchpad/ippen_moto"

# 新しく書く3か所のうち2つ（悩み・答え）と、頭の段の人の絵。元は各ページの「結論（ANSWER）」と目次の文
PAGES = {
    "dokugaku": dict(hito="hito_1_cost", q="養成講習は高いし、<br>独学で取れないかな…？", qs="テキストだけで受けられる？",
                     a='独学だけでは受験できないよ。受験資格がいるからね。でも、<b class="mark">試験の勉強そのものは独学でも進められる</b>よ。'),
    "how-to-choose": dict(hito="hito_5_mada", q="学校が多くて、<br>何から決めればいいの…？", qs="「おすすめ」を探す前に",
                          a='くらべる前に、<b class="mark">通学ゼロ・土日か夜・休んでも振替</b>の3つを決めておくと、続けられる学校にしぼれるよ。'),
    "kyufukin": dict(hito="hito_1_cost", q="給付金を使うと、<br>実質いくらになるの…？", qs="「最大80%」って本当？",
                     a='29.7万円の講座なら、修了しただけで半分が戻って<b class="mark">実質14.85万円</b>。条件をぜんぶ満たすと最大80%だよ。雇用保険に入っていた期間がないと対象にならないので、先に確かめよう。'),
    "merit-demerit": dict(hito="hito_5_mada", q="「やめとけ」って見て、<br>迷っている…", qs="本当に役に立たないの？",
                          a='「役に立たない」は半分本当。でも、<b class="mark">取る前から使い道が決まっている人</b>には、役に立つ資格だよ。'),
    "online": dict(hito="hito_3_yoru", q="家からオンラインで、<br>最後まで受けられる…？", qs="録画を見るだけでいいの？",
                   a='<b class="mark">家から修了まで受けられる講習</b>もあるよ。ただ、録画だけで修了できる講習は基本的になくて、ロールプレイはカメラとマイクをつけて、その場でやるよ。'),
    "training-and-exam-preparation": dict(hito="hito_4_support", q="養成講習を終えたら、<br>試験に受かるの…？", qs="対策講座って、別にいる？",
                                          a='養成講習は<b class="mark">受験の切符</b>、対策講座は<b class="mark">点の取り方</b>の練習。学校をくらべるときは、2つの合計で見ると安心だよ。'),
    "working-mothers": dict(hito="hito_2_donichi", q="子育てや仕事をしながら、<br>続けられるかな…", qs="子どもが熱を出したら？",
                            a='いちばん大事なのは<b class="mark">休んでも取り返せる振替</b>。つぎに、オンラインで子どもが画面に映ってもいいか。「休んでも大丈夫」な学校を選ぼう。'),
    "yasui": dict(hito="hito_1_cost", q="少しでも安い<br>養成講座はどこ…？", qs="全部でいくらかかるの？",
                  a='比較表の6校で総額なら<b class="mark">地域連携プラットフォーム（29.7万円）</b>。22講習ぜんぶの受講料だけなら、東京アカデミー（15万円・先着5名）だよ。'),
    "zaitaku-fukugyo": dict(hito="hito_3_yoru", q="資格を取ったら、<br>家で働けるかな…？", qs="副業や在宅の仕事は来る？",
                            a='<b class="mark">オンライン面談で、家から相談を受ける働き方</b>は選べるよ。ただ、相談に来てくれる人は、自分で見つけることになるよ。'),
    "zaitaku-kokka-shikaku": dict(hito="hito_3_yoru", q="家から出にくいけど、<br>国家資格を取れる…？", qs="どこまで家でできるの？",
                                  a='養成講習は<b class="mark">家から受けて修了できる学校</b>があるよ。でも試験は会場で、学科・論述の日と面接の日の、少なくとも2日は外に出るよ。'),
}

# 古い CSS から .gk の中に限って写す部品（guide-kit.css にない分）
OLD_PARTS = ["fact-table", "fact-row", "shindan", "notice-box", "honest-link", "setsumei-box", "kyufu-calc",
             "term-section-note", "kw-link", "mk", "txt-link", "button", "arw", "nb", "shikaku-cost-table",
             "guide-nextlink", "lead-intro", "disclosure", "visually-hidden"]
OLD_FILES = ["style.css", "picnic.css", "refine.css", "yomiyasu.css", "tone.css"]

MOYAN = "img/parts/t/moyan_school_hat_smile-200.webp"
SUNNY = "img/kata/sunny.webp"

PAGE_STYLE = """<style id="ippen-guide">
body.kata .gk{--gk-ink:var(--ink)}
body.kata .ps.chan .who .tag{display:inline-block;margin-left:6px;padding:0 7px;border-radius:999px;background:#fff;font-size:10.5px;letter-spacing:.06em;color:var(--sub)}
body.kata .pair + .src{margin-top:-14px}
body.kata .kakite{margin:0 0 36px;padding:20px 24px;border-radius:16px;background:#F8EFDC}body.kata .kk-t{margin:0;font-size:13px;font-weight:700;color:var(--sub);letter-spacing:.08em}body.kata .kk-d{margin:6px 0 0;font-size:14.5px;line-height:1.85}
body.kata .faq .qn{margin-right:8px;color:var(--link)}
body.kata .hb .gk>h3{margin-top:26px}
body.kata .lead2 .date{margin-top:6px}
body.kata .gk table{max-width:100%}
body.kata .gk .tblw,body.kata .gk .ys-table-wrap{overflow-x:auto}
</style>"""


# ---------- CSS ----------
def split_rules(css):
    """一番上のかたまり（rule か @media {...}）に分ける"""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        sel = css[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
            k += 1
        out.append((sel, css[j + 1:k - 1]))
        i = k
    return out


def want(sel):
    return any(re.search(r"\." + re.escape(c) + r"(?![a-z0-9])", sel) for c in OLD_PARTS)


def scope(sel):
    parts = []
    for s in sel.split(","):
        s = s.strip()
        if not s:
            continue
        if s.startswith(("html", "body", ":root")):
            m = re.match(r"(\S+)\s*(.*)", s)
            s = f"{m.group(1)} .gk {m.group(2)}".strip() if m.group(2) else None
            if s is None:
                continue
        else:
            s = ".gk " + s
        parts.append(s)
    return ",".join(parts)


OUTSIDE = ["cta-fab"]   # .gk の外（body の最後）に js が足す部品。そのままの形で写す


def outside(sel):
    return any(re.search(r"\." + re.escape(c) + r"(?![a-z0-9])", sel) for c in OUTSIDE)


def old_css():
    out = []
    root_vars = []
    for f in OLD_FILES:
        for sel, body in split_rules(open(os.path.join(CSS, f), encoding="utf-8").read()):
            if sel.startswith("@media"):
                inner = [f"{scope(s)}{{{b}}}" for s, b in split_rules(body) if want(s) and scope(s)]
                inner += [f"{s}{{{b}}}" for s, b in split_rules(body) if outside(s)]
                if inner:
                    out.append(f"{sel}{{{''.join(inner)}}}")
            elif sel.startswith("@"):
                continue
            elif sel.strip() == ":root":
                root_vars.append(body)
            elif outside(sel):
                out.append(f"{sel}{{{body}}}")
            elif want(sel) and scope(sel):
                out.append(f"{scope(sel)}{{{body}}}")
    head = "".join(f".gk,.cta-fab{{{b}}}" for b in root_vars)
    return head + "\n" + "\n".join(out)


def write_css():
    kit = open(os.path.join(CSS, "guide-kit.css"), encoding="utf-8").read()
    s = ("/* 新しい型の記事（/school-guides/）の中に残した、計算・診断・表などの部品の見た目。\n"
         "   scripts/ippen_build_guides.py が作る（手で直さない）。guide-kit.css の写し＋古い CSS からその部品の分だけ（.gk の中だけに効く） */\n"
         + kit + "\n/* ---- 古い CSS から（.gk の中だけ） ---- */\n" + old_css() + "\n")
    with open(os.path.join(CSS, "guide-kata.css"), "w", encoding="utf-8") as fh:
        fh.write(s)


# ---------- 本文 ----------
def txt(el):
    return re.sub(r"\s+", "", el.get_text("")) if el else ""


def inner(el):
    return "".join(str(c) for c in el.contents)


def convert_talk(soup, r):
    """mini-say → 新しい型の吹き出し"""
    for talk in soup.select(".gk-talk"):
        talk.name = "div"
        talk["class"] = ["pair"]
    for ms in soup.select(".mini-say"):
        cls = ms.get("class", [])
        bub = ms.select_one(".mini-say__bubble")
        name_b = bub.find("b") if bub else None
        tag = name_b.select_one(".mini-say__tag") if name_b else None
        tag_html = f'<span class="tag">{tag.get_text()}</span>' if tag else ""
        if tag:
            tag.extract()
        who = name_b.get_text() if name_b else ""
        if name_b:
            name_b.extract()
        body = inner(bub) if bub else ""
        av = ms.select_one(".mini-say__avatar img")
        if "mini-say--moyan" in cls:
            new = f'<div class="pm"><p><span class="who">{who}</span>{body}</p><img src="{r}{MOYAN}" alt="" loading="lazy" decoding="async"></div>'
        elif "mini-say--chan" in cls:
            src = av["src"] if av else f"{r}img/kata/hito_profile.webp"
            new = f'<div class="ps chan"><img src="{src}" alt="" loading="lazy" decoding="async"><p><span class="who">{who}{tag_html}</span>{body}</p></div>'
        else:
            new = f'<div class="ps"><img src="{r}{SUNNY}" alt="" loading="lazy" decoding="async"><p><span class="who">{who}{tag_html}</span>{body}</p></div>'
        frag = BeautifulSoup(new, "html.parser")
        if ms.parent and "pair" not in (ms.parent.get("class") or []):
            wrap = BeautifulSoup('<div class="pair"></div>', "html.parser").div
            wrap.append(frag)
            ms.replace_with(wrap)
        else:
            ms.replace_with(frag)
    for src in soup.select(".gk-talk__src"):
        src["class"] = ["src"]


def faq_html(sec):
    out = []
    for d in sec.select("details"):
        summ = d.find("summary")
        q = summ.select_one(".gk-qa__q,.ys-qa__q")
        if q:
            q.extract()
        qtext = inner(summ).strip()
        summ.extract()
        for m in d.select(".gk-qa__mark,.ys-qa__mark"):
            m.extract()
        a = d.select_one(".gk-qa__a,.ys-qa__a") or d
        out.append(f'<details><summary><b class="qn">Q</b>{qtext}</summary><div class="in">{inner(a).strip()}</div></details>')
        d.extract()
    return "".join(out)


def build(name, moto_dir):
    cfg = PAGES[name]
    path = f"school-guides/{name}/index.html"
    full = os.path.join(ROOT, path)
    moto = os.path.join(moto_dir, f"{name}.html")
    if not os.path.exists(moto):
        os.makedirs(moto_dir, exist_ok=True)
        shutil.copy(full, moto)
    src = open(moto, encoding="utf-8").read()
    r = P.rel_root(path)
    head_src, body_src = src.split("</head>", 1)

    # 頭：古い CSS と丸い字の指定を外し、新しい型の CSS を足す
    head = re.sub(r'<link rel="stylesheet" href="[^"]*css/cb-[^"]*"[^>]*>\n?', "", head_src)
    head = re.sub(r'<link rel="preload" href="[^"]*maru[^"]*"[^>]*>\n?', "", head)
    head = re.sub(r"<style>/\* 丸い文字.*?</style>\n?", "", head, flags=re.S)
    head = re.sub(r"(?<![\w-])\.kc(?=[\s{,:])", ".gk .kc", head)   # 計算のしかけの .kc を、パンくずの .kc と分ける
    add = "\n".join([F.FONTS, f'<link rel="stylesheet" href="{r}css/kata.css?v=2026.1120">',
                     f'<link rel="stylesheet" href="{r}css/guide-kata.css?v=2026.1120">', PAGE_STYLE, F.H1_SP])
    kyo = P.css_link(path)
    head = head.replace(kyo, add + "\n" + kyo) if kyo in head else head + add + "\n" + kyo + "\n"

    soup = BeautifulSoup(body_src, "html.parser")
    art = soup.find("article")
    crumb = soup.select_one(".kc")
    crumb_html = str(crumb) if crumb else ""
    scripts = [str(s) for s in BeautifulSoup(src, "html.parser").find_all("script", src=True)
               if "/js/" in s["src"] or s["src"].startswith("../")]
    wrap_cls = " ".join(c for c in art.get("class", []) if c not in ("container", "container--article", "guide-article"))
    if "gk" not in wrap_cls.split():
        wrap_cls = ("gk " + wrap_cls).strip()

    convert_talk(art, r)
    hdr = art.select_one(".article-header")
    h1 = hdr.find("h1")
    cat = hdr.select_one(".article-card__category")
    lede = hdr.select_one(".article-header__lede")
    date = hdr.select_one(".updated-date")
    toc = art.select_one(".gk-toc,.ys-toc")
    ans = art.select_one(".gk-answer,.ys-answer")
    disc = art.select_one("details.disclosure")
    intro = art.select_one(".lead-intro")

    # 1 ヒーロー
    hero = f"""<section class="hero1"><div class="w">
  <p class="eye">{cat.get_text().strip() if cat else ""}</p>
  <h1>{inner(h1)}</h1>
  <div class="hstage">
    <img class="garl" src="{r}img/kata/sora_garland.webp" alt="" aria-hidden="true">
    <img class="cld c1" src="{r}img/parts/01_sky_cloud_left.webp" alt="" aria-hidden="true">
    <img class="cld c2" src="{r}img/parts/03_sky_cloud_right.webp" alt="" aria-hidden="true">
    <p class="qb"><span class="lb">このページで答える悩み</span>{cfg["q"]}<br><small>{cfg["qs"]}</small></p>
    <div class="who1" aria-hidden="true">
      <span class="hm m1">？</span><span class="hm m2">？</span>
      <span class="mpic"><img class="hito" src="{r}img/kata/{cfg["hito"]}.webp" alt=""></span>
    </div>
    <img class="deco tent" src="{r}img/parts/t/13_blue_yellow_tent-136.webp" alt="" aria-hidden="true">
    <img class="deco fl1" src="{r}img/parts/t/23_flowers_left_group-180.webp" alt="" aria-hidden="true">
    <img class="deco fl2" src="{r}img/parts/t/25_flowers_right_group-180.webp" alt="" aria-hidden="true">
    <img class="deco bu1" src="{r}img/parts/t/24_bush_lower_left-136.webp" alt="" aria-hidden="true">
    <img class="deco bu2" src="{r}img/parts/t/26_bush_lower_right-136.webp" alt="" aria-hidden="true">
  </div>
  <i class="oka" aria-hidden="true"></i>
</div></section>"""

    # 2 答え：いまの「結論」の見出しを h2 に、サニー先生の1行（新しく書く）、いまの丸い3つ・注はそのまま
    at = ans.select_one(".gk-answer__t,.ys-answer__t")
    h2a = inner(at) if at else "結論"
    for x in ans.select(".gk-answer__k,.ys-answer__k,.gk-answer__t,.ys-answer__t"):
        x.extract()
    kotae = f"""<section class="sec2 green" id="kotae"><div class="w nar">
  <p class="eye c">答え</p>
  <h2 class="c">{h2a}</h2>
  <div class="sun2">
    <img src="{r}{SUNNY}" alt="サニー先生" loading="lazy" decoding="async">
    <p class="sb"><span class="who">サニー先生</span>{cfg["a"]}</p>
  </div>
  <div class="{wrap_cls}">{inner(ans)}</div>
</div></section>"""

    # 3 目次とリード：目次の1行は、いまの目次の小さい行（答えの言い方の行）
    lis, tsub = [], ""
    for li in toc.select("li"):
        a = li.find("a")
        if a["href"] == "#faq":   # よくある質問は、比較表と同じく目次の下の小さい行へ
            tsub = '<p class="tsub"><a href="#faq">よくある質問</a></p>'
            continue
        sm = li.find("small")
        b = li.find("b")
        t = (sm or b).get_text().strip()
        lis.append(f'<li><a href="{a["href"]}"><span class="tn">{len(lis) + 1}</span><span class="tx">{t}</span></a></li>')
    lead = []
    if lede:
        lead.append(f"<p>{inner(lede)}</p>")
    if intro:
        lead.append(f'<div class="{wrap_cls}">{str(intro)}</div>')
    if date:
        lead.append(f'<p class="date">{" ".join(inner(s) for s in date.find_all("span", recursive=False)) or inner(date)}</p>')
    if disc:
        lead.append(f'<div class="{wrap_cls}">{str(disc)}</div>')
    mokuji = f"""<section class="sec2" id="mokuji"><div class="w nar">
  <nav class="toc toc3" aria-label="このページの目次"><p class="tt">このページでわかること</p><ol>{"".join(lis)}</ol>{tsub}</nav>
  <div class="lead2">{"".join(lead)}</div>
</div></section>"""
    for x in (hdr, toc, ans, disc, intro):
        if x:
            x.extract()

    # 4 本文の節・まとめ・よくある質問・次の一歩・書いた人
    secs, matome, faq, tsugi, kakite = [], [], "", "", ""
    n = 0
    for el in list(art.children):
        if isinstance(el, NavigableString):
            continue
        cls = el.get("class") or []
        if el.name == "section" and "guide-section" in cls and el.get("id") == "faq":
            h2 = el.find("h2")
            ht = inner(h2) if h2 else "よくある質問"
            if h2:
                h2.extract()
            qa = faq_html(el)
            for x in el.select(".gk-faq,.ys-faq"):
                if not txt(x):
                    x.extract()
            rest = inner(el).strip()
            faq = (f'<section class="sec2" id="faq"><div class="w nar">' + ('' if txt(BeautifulSoup(ht, "html.parser")) == "よくある質問" else '<p class="eye c">よくある質問</p>') + f'<h2 class="c">{ht}</h2>'
                   + (f'<div class="{wrap_cls}">{rest}</div>' if rest else "") + f'<div class="faq">{qa}</div></div></section>')
        elif el.name == "section" and "guide-section" in cls:
            n += 1
            h2 = el.find("h2")
            for im in h2.select("img.sec-illust"):
                im.extract()
            ht = inner(h2).strip()
            h2.extract()
            secs.append(f'<section class="sec2 hb" id="{el["id"]}"><div class="w nar">\n  <p class="eye">くわしく {n}</p>\n'
                        f'  <h2>{ht}</h2>\n  <div class="{wrap_cls}">{inner(el)}</div>\n</div></section>')
        elif el.name == "section" and "related" in cls:
            h2 = el.find("h2")
            cards = []
            for a in el.select("a"):
                ty = a.select_one(".related__type")
                ti = a.select_one(".related__item-title")
                cards.append(f'<a class="ncard" href="{a["href"]}"><span class="nn">{ty.get_text().strip() if ty else ""}</span>'
                             f'<span class="tl">{inner(ti).strip() if ti else a.get_text().strip()}</span></a>')
            tsugi = (f'<section class="sec2" id="tsugi"><div class="w">\n  <p class="eye c">次の一歩</p>\n  <h2 class="c">{inner(h2)}</h2>\n'
                     f'  <div class="next3">{"".join(cards)}</div>\n</div></section>')
        elif el.name == "aside" and "author-profile" in cls:
            nm = el.select_one(".author-profile__name")
            for im in nm.select("img"):
                im.extract()
            bio = el.select_one(".author-profile__bio")
            link = [p for p in el.find_all("p") if p.find("a")]
            kakite = (f'<div class="kakite" id="kakite"><p class="kk-t">{inner(nm).strip()}</p><p class="kk-d">{inner(bio)}</p>'
                      + (f'<p class="kk-d">{inner(link[-1])}</p>' if link else "") + "</div>")
        else:
            matome.append(str(el))
    mat = (f'<section class="sec2" id="matome"><div class="w nar"><div class="{wrap_cls}">{"".join(matome)}</div></div></section>'
           if matome else "")
    kk = f'<section class="sec2" id="shutten"><div class="w nar">{kakite}</div></section>' if kakite else ""

    # いちばん下の「次の段」（学校えらびの側＝段2。知る＝段1、稼ぐ＝段6）
    step = P.way_step(path)
    if step == 1:
        nxt_now, nxt_go, back = '段1「知る」', '<span class="stepno">2</span><a href="/schools/compare/">続けられる学校を、6校の比較表でしぼる</a> →', ""
    elif step == 6:
        nxt_now, nxt_go, back = None, None, None
    else:
        nxt_now, nxt_go, back = '段2「学校選び」', '<span class="stepno">3</span><a href="/start/">入学が決まったら、試験までの勉強の道へ</a> →', '<p class="back"><a href="/careers/">← 前の段「知る」にもどる</a></p>'
    picnic = f"""<section class="picnic" aria-hidden="true"><div class="kscene">
  <img class="flags2" src="{r}img/kata/sora_garland.webp" alt="" loading="lazy" decoding="async">
  <img class="pic" src="{r}img/kata/hero_picnic.webp" alt="" loading="lazy" decoding="async">
</div></section>"""
    nxt = (f"""<section class="nxt"><div class="w">
  <div class="box"><img src="{r}{SUNNY}" alt="" loading="lazy" decoding="async"><div><p class="now">いまは {nxt_now}。次は</p><p class="go">{nxt_go}</p></div><p class="more" style="margin:0;font-size:13.5px"><a class="tl" href="#sitemap">キャリコンへの道を、ぜんぶ見る</a></p></div>
  {back}
</div></section>""" if nxt_now else "")

    svg = re.search(r'<svg width="0" height="0".*?</svg>', open(os.path.join(ROOT, "school-guides/kyufukin-tetsuzuki/index.html"), encoding="utf-8").read(), re.S).group(0)
    main = "\n\n".join(x for x in [hero, kotae, mokuji, *secs, mat, faq, kk, tsugi] if x)
    body = ("<body class=\"kata\">\n" + svg + "\n" + P.top_parts(path, crumb_html)
            + '<main id="main">\n' + main + "\n</main>\n" + picnic + "\n" + nxt + "\n" + P.end_parts(path)
            + "\n".join(scripts) + "\n</body>\n</html>\n")
    out = soroe(head + "</head>\n" + body)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(out)
    return src, out


def chunks(html, new):
    """本文の文字を、ブロック（p・li・見出し・表のます など）ごとの文にする（並びが変わっても比べられるように）"""
    s = BeautifulSoup(html, "html.parser")
    root = s.find("main") if new else s.find("article")
    for x in root.select("script,style"):
        x.extract()
    if not new:
        # 目次は「答えの1行」に作りかえる所（新しく書く3か所の1つ）。英字の小見出し（ANSWER・CONTENTS）は外す
        for x in root.select(".gk-toc,.ys-toc,.gk-answer__k,.ys-answer__k,.gk-qa__q,.gk-qa__mark,.ys-qa__q,.ys-qa__mark"):
            x.extract()
    else:
        for x in root.select(".toc3,.qb,.sun2,.hb>.w>.eye,#kotae>.w>.eye,#faq>.w>.eye,#tsugi .eye,.faq .qn"):
            x.extract()
    out = []
    for el in root.find_all(["p", "li", "h1", "h2", "h3", "h4", "dt", "dd", "td", "th", "summary", "small", "b", "span", "a", "figcaption", "label", "option", "button"]):
        if el.find(["p", "li", "h2", "h3", "td", "summary", "div"]):
            continue
        t = re.sub(r"\s+", "", el.get_text(""))
        if t:
            out.append(t)
    return out, re.sub(r"\s+", "", root.get_text(""))


def compare(name, before, after):
    a, at = chunks(before, False)
    b, bt = chunks(after, True)
    lost = [x for x in dict.fromkeys(a) if x not in bt]
    added = [x for x in dict.fromkeys(b) if x not in at]
    return sum(map(len, lost)), sum(map(len, added)), [("消えた", x) for x in lost] + [("足した", x) for x in added]


# ---------- ほかのページ（トップ・学校ページ・給付金の手続き）と見た目をそろえる（11/20 ちゃん「他のページとあってる？」） ----------
# 指示書_試験の側 25〜28：段の地は 芝生・白・あお・スタンプ の4つ／道具の段は「あお」／次の一歩は「スタンプ」1回／段の切りかえは波線／
# 太字の代わりに黄色の印／ボタンは行き先1〜2つの所だけオレンジのカプセル（kata.css の .cta と同じ形）
TOOLS = ("gk-check", "kyufu-calc", "kyufu-check", "shindan", "guide-check")
WAVE_W = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 40' preserveAspectRatio='none'%3E"
          "%3Cpath d='M0 24 Q100 6 200 24 T400 24 T600 24 T800 24 T1000 24 T1200 24 V40 H0 Z' fill='%23ffffff'/%3E%3C/svg%3E")
SOROE_STYLE = """<style id="ippen-guide-soroe">
/* 道具の段（チェックリスト・計算・診断）は「あお」の地。上下は kata.css の波線 */
body.kata section.sec2.hb.sky{padding-top:100px!important;padding-bottom:92px!important}
body.kata .sky .gk-check{background:#fff!important;border:0!important;border-radius:22px!important;padding:4px 22px!important}
body.kata .sky .gk-check li{border-top-color:var(--line)!important}
/* 次の一歩は「スタンプ」の地。中身は白い面にのせる（トップの #nayami と同じ形） */
body.kata section.sec2.gara#tsugi{background:#fff url("../../img/kata/gara_kimete.webp") center top/780px auto repeat!important;padding:104px 0 112px!important}
body.kata section.sec2.gara#tsugi>.w{background:#fff;border-radius:26px;box-shadow:0 0 20px 22px #fff;padding-top:34px;padding-bottom:40px}
body.kata section.sec2.gara#tsugi .ncard{background:#fff}
body.kata section.sec2.gara#tsugi::before,body.kata section.sec2.gara#tsugi::after{content:""!important;position:absolute;left:0;right:0;height:40px;z-index:2;background:url("WAVE") no-repeat!important;background-size:100% 40px!important;pointer-events:none}
body.kata section.sec2.gara#tsugi::before{top:-1px;transform:scaleY(-1)}
body.kata section.sec2.gara#tsugi::after{bottom:-1px}
/* 出典・注は小さな字（ほかのページの .src と同じ 13px） */
body.kata .hb .gk p.src,body.kata .gk .term-section-note{font-size:13px!important;line-height:1.8!important;color:var(--sub)!important}
/* 強めたい所は黄色の印（太字だけにしない） */
body.kata .gk strong{padding:0 2px;background:linear-gradient(transparent 60%,#FFEDA6 60%,#FFEDA6 94%,transparent 94%)}
/* 古い部品を新しい型の形に：注意の箱・正直な話・説明会の箱・ボタン・広告の開示 */
body.kata .gk .notice-box{max-width:none!important;margin:0 0 36px!important;text-align:left!important}
body.kata .gk .notice-box p{font-size:13px!important;line-height:1.8!important;color:var(--sub)!important}
body.kata .gk .honest-link{max-width:none!important;margin:0 0 40px!important;padding:24px 28px!important;background:#fff!important;border:1px solid var(--line)!important;border-radius:22px!important;text-align:left!important}
body.kata .gk .honest-link__label{margin:0 0 8px!important;font-size:13px!important;font-weight:700;letter-spacing:.1em;color:var(--sub)!important}
body.kata .gk .honest-link__body{font-size:15.5px!important;line-height:2!important;color:var(--ink)!important}
body.kata .gk .honest-link__act a{font-size:15px!important}
body.kata .gk .setsumei-box{max-width:none!important;margin:40px 0 0!important;padding:30px 28px!important;background:#fff!important;border:1px solid var(--line)!important;border-radius:22px!important;box-shadow:none!important;text-align:center}
body.kata .gk .setsumei-box__t{font-size:18px;color:var(--ink);margin:0 0 8px}
body.kata .gk .setsumei-box p{font-size:15.5px;line-height:2}
body.kata .gk .button--primary{display:block;width:100%;max-width:360px;margin:0 auto;box-sizing:border-box;padding:14px 22px;border:1px solid #E07A4F;border-radius:999px;background:#E8865B;color:#fff;box-shadow:0 3px 0 #D06E45;font-size:15px;font-weight:700;line-height:1.5;letter-spacing:.04em;text-align:center;white-space:normal!important;text-decoration:none;transform:none}
body.kata .gk .button--primary:hover{background:#E07A4F;box-shadow:0 3px 0 #D06E45;transform:none}
body.kata .gk .button--primary[disabled]{opacity:.45;box-shadow:none}
body.kata .gk .kc__go{max-width:360px;margin:22px auto 0;border:1px solid #E07A4F;background:#E8865B;box-shadow:0 3px 0 #D06E45;font-size:15px;letter-spacing:.04em}
body.kata .gk .kc__go:hover{background:#E07A4F}
body.kata .gk details.disclosure .disclosure__more{color:var(--link)!important}
@media (max-width:760px){
body.kata section.sec2.hb.sky{padding-top:64px!important;padding-bottom:60px!important}
body.kata section.sec2.gara#tsugi{background-size:560px auto!important;padding:72px 0 80px!important}
body.kata section.sec2.gara#tsugi>.w{box-shadow:0 0 12px 12px #fff;padding-top:24px;padding-bottom:28px}
body.kata section.sec2.gara#tsugi::before,body.kata section.sec2.gara#tsugi::after{height:24px;background-size:100% 24px!important}
body.kata .gk .honest-link,body.kata .gk .setsumei-box{padding:20px 18px!important}
}
</style>""".replace("WAVE", WAVE_W)


def _h1_br(html):
    """11/20 ちゃん：how-to-choose の見出しは「選び方 —」で改行"""
    html = html.replace("選び方 <wbr/>—<wbr/> <wbr/>比較する前に", "選び方 —<br>比較する前に")
    return html.replace("選び方 — 比較する前に", "選び方 —<br>比較する前に")


# 11/20 ちゃん「長い見出しは短くしてください。ただし意味はちゃんとわかるように。また、SEOにも配慮してください」
# スマホ375で3行以上になった h1・h2 だけを短くする（前→後は 1119_本番いっぺんの計画.md の「11/20 見出しを短く」）。
# 検索の題（title・説明文・og:title・構造化データの headline）は本番のまま長い。
# 鍵＝いまの見出しの文字（空白を除く）。値＝新しい見出し（<wbr>・<br> は改行してよい所）
MIDASHI = {
    # h1
    "キャリアコンサルタント養成講座の選び方—比較する前に決めておく3つのこと":
        "養成講座の<wbr>選び方 —<br>比べる前に<wbr>決める<wbr>3つのこと",
    "キャリアコンサルタント養成講座の給付金—教育訓練給付金「最大80%」で実質いくら？":
        "養成講座の<wbr>給付金 —<br>最大80%で<wbr>実質いくら？",
    "キャリアコンサルタント養成講座はオンラインで受けられる？—選び方と確認ポイント":
        "養成講座は<wbr>オンラインで<wbr>受けられる？",
    "キャリアコンサルタント養成講座が安いのはどこ？全22講習の受講料と給付金で実質いくら":
        "養成講座が<wbr>安いのはどこ？<br>全22講習の<wbr>受講料と<wbr>実質の負担",
    "キャリアコンサルタント養成講座は子育て中・働きながらでも通える？":
        "養成講座は、<wbr>子育て中・<br>働きながらでも<wbr>通える？",
    "キャリアコンサルタントは役に立たない・やめとけ？—やめたほうがいい人もいます":
        "キャリアコンサルタントは<br>役に立たない・<wbr>やめとけ？",
    # h2
    "まず知っておくこと:どの養成講習も「厚生労働大臣認定」":
        "どの養成講習も<wbr>「厚生労働大臣認定」",
    "養成講座の選び方3:総費用の上限(試験対策まで含めて)":
        "養成講座の選び方3:<wbr>総費用の上限<wbr>(試験対策込み)",
    "教育訓練給付金の「最大80%」は3段階の合計。無条件ではありません":
        "給付金の<wbr>「最大80%」は、<wbr>3段階の合計",
    "給付金を受けるには、受講開始の2週間前までにやることがあります":
        "給付金は、<wbr>受講開始の<wbr>2週間前までに<wbr>手続きが必要",
    "そもそもキャリアコンサルタントって、何をする人？":
        "キャリアコンサルタントって、<wbr>何を<wbr>する<wbr>人？",
    "①独占業務がない—資格がなくても同じ仕事ができます":
        "①独占業務がない&nbsp;—<br>資格なしでも<wbr>できます",
    "それでもキャリアコンサルタント資格を取る価値がある人":
        "それでも<wbr>資格を<wbr>取る価値が<wbr>ある人",
    "オンライン養成講座のライブ型と録画(オンデマンド)型の違い":
        "ライブ型と<wbr>録画(オンデマンド)型の<wbr>違い",
    "オンラインの養成講座に向く人・向かない可能性がある人":
        "オンライン受講に<wbr>向く人・<wbr>向かない<wbr>可能性がある人",
    "子育て・仕事と養成講座の両立でいちばん困るのは「欠席できない仕組み」":
        "両立で<wbr>いちばん<wbr>困るのは<wbr>「欠席できない仕組み」",
    "運営者の考え：トータルで見ると、地域連携プラットフォームをすすめます":
        "運営者の<wbr>おすすめ：<wbr>地域連携<wbr>プラットフォーム",
}
def _midashi(html):
    """長い h1・h2 を短い形に（何回かけても同じ）。
    h1 から「キャリアコンサルタント」が外れたページは、すぐ上の小さな1行（eye）を「キャリアコンサルタント養成講座ガイド」に"""
    def one(m):
        key = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", m.group(3)))
        if key not in MIDASHI:
            return m.group(0)
        return f"<{m.group(1)}{m.group(2)}>{MIDASHI[key]}</{m.group(1)}>"
    html = re.sub(r"<(h1|h2)\b([^>]*)>(.*?)</\1>", one, html, flags=re.S)
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, re.S)
    if h1 and h1.group(1) in MIDASHI.values() and "キャリアコンサルタント" not in re.sub(r"<[^>]+>", "", h1.group(1)):
        html = re.sub(r'(<section class="hero1"><div class="w">\s*<p class="eye">)養成講座ガイド(</p>)',
                      r"\1キャリアコンサルタント養成講座ガイド\2", html, count=1)
    return html


def soroe(html):
    """組んだあとのページに、そろえの手直しを入れる（何回かけても同じ結果）"""
    html = _midashi(_h1_br(html))
    html = re.sub(r'<style id="ippen-guide-soroe">.*?</style>\n?', "", html, flags=re.S)
    html = html.replace("</head>", SOROE_STYLE + "\n</head>", 1)
    # 段の地：道具がある「くわしく」の段を あお に（あおが続くときは先の1つだけ）
    parts = re.split(r'(?=<section class="sec2)', html)
    prev_sky = False
    for i, p in enumerate(parts):
        m = re.match(r'<section class="(sec2[^"]*)"', p)
        if not m:
            continue
        cls = m.group(1).split()
        end = p.find("</section>")
        body = p[:end] if end >= 0 else p
        has_tool = any(f'class="{t}' in body for t in TOOLS)
        if "hb" in cls and has_tool and not prev_sky and "sky" not in cls:
            cls.append("sky")
        if 'id="tsugi"' in p[:80] and "gara" not in cls:
            cls.append("gara")
        parts[i] = p.replace(m.group(0), f'<section class="{" ".join(cls)}"', 1)
        prev_sky = "sky" in cls
    # 11/20 ちゃん「見出しの改行も調整して」：見出しを文節で折る印（ippen_yomiyasu・何回かけても同じ）
    return Y.apply("".join(parts))


def soroe_files(names):
    for nm in names:
        f = os.path.join(ROOT, f"school-guides/{nm}/index.html")
        s = open(f, encoding="utf-8").read()
        t = soroe(s)
        if t != s:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(t)
        print(nm, "そろえ", "直した" if t != s else "変化なし")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--soroe" in args:   # 組み直さずに、いまのページへ そろえ だけ入れる
        soroe_files([a for a in args if a != "--soroe"] or list(PAGES))
        sys.exit(0)
    moto = MOTO
    if "--moto" in args:
        i = args.index("--moto")
        moto = args[i + 1]
        del args[i:i + 2]
    verbose = "-v" in args
    args = [a for a in args if a != "-v"]
    write_css()
    for nm in args or PAGES:
        before, after = build(nm, moto)
        d, i, pieces = compare(nm, before, after)
        print(f"{nm}: 消えた字 {d}・足した字 {i}")
        if verbose:
            for p in pieces:
                print("   ", p)
