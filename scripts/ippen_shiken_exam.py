#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：試験の側の一枚もの3ページ（01 試験の入口 /exam/・02 試験対策の記事
/exam-guide/gakka-benkyoho/・03 コラム /column/kimerarenai-yoru/）を、ラフ_1119 の型で組む道具。

- 骨組みはラフの本文（LEC と同じやり方）。中の文は本番の文にもどす（ラフで言いかえた所を本番の言葉に）
- 本番にあってラフにない文は、本番の言葉のまま「くわしく」の箱（details）などに残す
- head・構造化データは本番から（ippen_shiken.page）。パンくずの構造化データだけ新しい並びに
- 03 コラムは、ちゃんの 11/19 の指示（「ちゃんと状況も書いて欲しい…調査して、まとめて」）で書き直した
  ラフの本文を使う（1119_コラム_協議会とJCDA_調べたこと.md。出典はすべて公式・11/19 確認）

使い方: python3 scripts/ippen_shiken_exam.py [01 02 03]
"""
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_shiken as S  # noqa: E402

ROOT = P.ROOT


def prod(path):
    """本番（このブランチの最初の版＝origin/main 由来）のページ。何度回しても同じものから組む"""
    return subprocess.run(["git", "-C", ROOT, "show", "f1bfc3922:" + path], capture_output=True, text=True, check=True).stdout


def sub(body, a, b, count=1):
    """1か所ずつ入れかえる（見つからなければ止める）"""
    if hasattr(a, "subn"):
        new, n = a.subn(b, body, count=count)
    else:
        n = body.count(a)
        new = body.replace(a, b, count) if n else body
    if not n:
        raise SystemExit(f"見つからない: {str(a)[:120]}")
    return new


def inner(el):
    return "".join(str(c) for c in el.contents) if el else ""


def h2(soup, text):
    """見出しの文で h2 をさがす（本番の見出しは <wbr> 入り）"""
    for el in soup.find_all("h2"):
        if text in el.get_text():
            return el
    raise SystemExit("h2 がない: " + text)


def nowbr(s):
    return s.replace("<wbr>", "").replace("<wbr/>", "")


def ld_breadcrumb(path, crumb):
    def fix(ld):
        out = []
        for j in ld:
            if '"BreadcrumbList"' in j:
                items = ",".join('{"@type":"ListItem","position":%d,"name":"%s","item":"https://carepicnic.com%s"}' % (
                    i + 1, n, (h or P.url_of(path)).split("#")[0]) for i, (n, h) in enumerate(crumb))
                j = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{items}]}}</script>'
            out.append(j)
        return out
    return fix


def finish(path, html, cat, crumb, extra_css=(), scripts=()):
    body_scripts = "\n".join(scripts)
    if body_scripts:
        html = html.replace("@@END@@\n", "@@END@@\n" + body_scripts + "\n", 1)
    src = prod(path)
    out = S.page(path, src, html, cat=cat, crumb=crumb, extra_css=extra_css, ld_fix=ld_breadcrumb(path, crumb))
    S.check(path, out)
    return out


# =============================================================== 02 試験対策の記事
def build_02():
    path = "exam-guide/gakka-benkyoho/index.html"
    r = P.rel_root(path)
    soup = BeautifulSoup(prod(path), "html.parser")
    rows = soup.select("table.gk-table tbody tr")
    b = S.rough_body("02", path)

    # 頭：記事の型（小山に悩む人）。eye は本番の h1
    b = sub(b, '<section class="hero1 x-uhero">', '<section class="hero1">')
    b = sub(b, '<p class="x-tagline"><span class="x-step-tag">勉強の道 STEP1 試験を知る</span></p>',
            '<p class="x-tagline"><a class="x-step-tag" href="/exam/#s1">勉強の道 STEP1 試験を知る</a></p>')
    b = sub(b, '<p class="eye">キャリコン学科試験の勉強法（問題番号でわかる出題傾向と対策）</p>',
            '<p class="eye">キャリコン学科試験の効率的な勉強法 — 問題番号でわかる出題傾向と対策</p>')

    # 答え：本番の結論の文
    b = sub(b, re.compile(r'<p class="sb"><span class="who">サニー先生</span>.*?</p>', re.S),
            '<p class="sb"><span class="who">サニー先生</span>効率よく勉強するコツは、<b class="mark">過去問を解いて、自分が落としやすい分野を見つけ、そこを集中して補強すること</b>です。</p>')
    b = sub(b, '<p class="src c">出典：キャリアコンサルティング協議会「受験概要」「過去問題」（第30回・第31回・第32回 学科試験。2026年9月29日に確かめました）</p>',
            '<p class="c x-fact-t">キャリアコンサルタントの学科試験は、全50問・四肢択一のマークシート方式です。試験時間は100分で、100点満点（1問2点）のうち70点以上で合格です。</p>\n'
            '  <p class="src c">出典：キャリアコンサルティング協議会「受験概要」「過去問題」（第30回・第31回・第32回 学科試験。2026年9月29日に確かめました）</p>')

    # 目次の下：本番のリード（更新日も）
    b = sub(b, '<p>過去問3回分（第30〜32回）を1問ずつ確かめて、「何番に、どの分野が出るか」を表にまとめました。</p>',
            '<p>過去問3回分（第30〜32回）を1問ずつ確かめて、「何番に、どの分野が出るか」を表にまとめました。</p>\n    <p class="x-upd">更新日：2026年10月2日</p>')

    # くわしく1：本番の見出しと文の並びに（モヤンの問い → 本文 → サニー先生）
    b = sub(b, "<h2>問題番号でわかる、分野の並び</h2>", "<h2>問題番号ごとの出題傾向と対策ポイント</h2>")
    b = sub(b, '<p>番号は回によって2〜3問前後しますが、流れは毎回ほぼ同じです。</p>',
            '<p>そのため、問題番号を見れば、どの分野の問題かがだいたいわかります。番号は回によって2〜3問前後しますが、流れは毎回ほぼ同じです。</p>\n'
            f'    <div class="pair" style="margin:22px 0 0"><div class="ps"><img src="{r}img/kata/sunny.webp" alt="サニー先生"><p><span class="who">サニー先生</span>問題の並びは<b class="mark">「出題範囲」の順番どおり</b>なんだ。だから、間違えた問題の番号を見れば、<b class="mark">苦手な分野がわかる</b>よ。</p></div></div>')
    # 分野ごとの帯：出たテーマ（ことば図鑑・理論家図鑑へのリンクつき）と 1問1答のリンクは本番の表から
    det = re.findall(r"<details[^>]*>.*?</details>", b, re.S)
    assert len(det) == len(rows) == 10, (len(det), len(rows))
    for d, tr in zip(det, rows):
        tds = tr.find_all("td")
        themes = inner(tds[0].select_one(".gk-themes"))
        a = tds[1].select_one("a.domain-drill")
        nd = re.sub(r'(<span class="lb">出たテーマ</span>).*?(</p>)', lambda m: m.group(1) + themes + m.group(2), d, count=1, flags=re.S)
        nd = re.sub(r'<a class="tl" href="#">', f'<a class="tl" href="{a["href"]}">', nd, count=1)
        b = b.replace(d, nd, 1)
    b = sub(b, '<p class="hint">※番号の範囲は回によって前後するため、一部重なっています。</p>',
            '<p class="hint">※番号の範囲は回によって前後するため、一部重なっています。表の中のリンクから、このサイトのことば図鑑・理論家図鑑に移動できます。</p>')
    b = sub(b, '<p><span class="who">モヤン</span>分身しなくてよかった〜！ 表を見れば、問題が多い分野がひと目でわかるね。</p>',
            '<p><span class="who">モヤン</span>分身しなくてよかった〜！表を見れば、問題が多い分野がひと目でわかるね。</p>')

    # くわしく2：3ステップの文は本番の文
    b = sub(b, '<p class="lead1">最初は解けなくても大丈夫。<b class="mark">間違えた問題を分野ごとに数える</b>と、弱点がはっきり見えます。</p>',
            '<p class="lead1">「理論で3問」「労働市場で4問」のように数えると、<b class="mark">弱点がはっきり見えます</b>。</p>')
    b = sub(b, '<li class="st"><p class="fw">今の実力をつかむ</p><h3>直近の過去問（3〜5回分）を、本番どおり100分で解く</h3><p>過去問は、協議会のサイトで無料で公開されています。</p></li>',
            '<li class="st"><p class="fw">ステップ1</p><h3>直近の過去問（3〜5回分）を、本番どおり100分で解く</h3><p>最初は解けなくても大丈夫です。今の実力と、試験の雰囲気をつかみましょう。過去問は、<a class="tl" href="https://www.career-shiken.org/about/learninfo/" rel="noopener nofollow" target="_blank">キャリアコンサルティング協議会のサイト</a>で無料で公開されています。</p></li>')
    b = sub(b, '<li class="st key"><p class="fw">弱点を見つける</p><h3>間違えた問題を「分野ごと」に数える</h3><p>上の図を使って、どの分野に多いかを数えます。</p></li>',
            '<li class="st key"><p class="fw">ステップ2</p><h3>間違えた問題を「分野ごと」に数える</h3><p>上の表を使って、間違えた問題がどの分野に多いかを数えます。問題番号は回によってずれるので、番号ではなく分野で数えるのがおすすめです。</p></li>')
    b = sub(b, '<li class="st"><p class="fw">しぼって補強</p><h3>苦手な分野にしぼって補強する</h3><p>下の「あなたの苦手は？」から選べます。</p></li>',
            '<li class="st"><p class="fw">ステップ3</p><h3>苦手な分野にしぼって補強する</h3><p>下の「あなたの苦手は？」から選べます。</p></li>')
    b = sub(b, re.compile(r'(<div class="ps"><img src="[^"]+" alt="サニー先生"><p><span class="who">サニー先生の解説</span>問題番号は回によってずれるんだ。.*?</div>)', re.S),
            lambda m: m.group(1) + f'\n      <div class="pm"><p><span class="who">モヤン</span>「理論で3問」みたいに数えるんだね！弱点がはっきり見えてきたよ。</p><img src="{r}img/parts/t/moyan_school_hat_smile-200.webp" alt="モヤン"></div>')

    # あなたの苦手は？：本番の「ステップ3」と「このサイトで補強するなら」の文とリンク
    ul = h2(soup, "このサイトで補強するなら").find_next("ul")
    more = re.sub(r'href="\.\./\.\./', 'href="/', str(ul)).replace('href="../', 'href="/exam-guide/').replace('class="txt-link"', 'class="tl"')
    b = sub(b, '<p class="src c">補強のしかたは、上の表の「対策」と、本文の3ステップから</p>',
            f'<div class="x-hokyo"><p class="tt">このサイトで補強するなら</p>{more}</div>')
    js_data = """var D={
riron:{t:'理論家',tip:'理論家とキーワードをセットで覚える。シャイン・サビカス・クランボルツは続けて出題されている',l:[['理論家図鑑','/theorists/'],['理論家の覚え方','/theorists/oboekata/'],['この分野の1問1答を解く（493問）','/games/quiz/?g=dom:2']]},
toukei:{t:'統計・白書',tip:'「労働経済の分析」「能力開発基本調査」の概要版で、数字の傾向（増えたか・減ったか）を押さえる。',l:[['試験に出る資料の要点','/exam-guide/shiryo/'],['労働法・統計・制度','/laws/']]},
hou:{t:'法律・制度',tip:'数字と「義務か努力義務か」を中心に、整理ノートを作る。',l:[['ことば図鑑','/terms/'],['労働法・統計・制度','/laws/'],['この分野の1問1答を解く（119問）','/games/quiz/?g=dom:5']]},
soudan:{t:'相談の技能',tip:'相談の流れ（関係づくり → 問題の把握 → 目標設定 → 方策の実行 → 評価・終了）を図にして、各段階でやることを書き出す。',l:[['この分野の1問1答を解く（166問）','/games/quiz/?g=dom:9'],['ことば図鑑','/terms/']]},
rinri:{t:'倫理',tip:'「キャリアコンサルタント倫理綱領」を一度通して読む。',l:[['キャリアコンサルタント倫理綱領（ことば図鑑）','/terms/rinri-koryo/'],['この分野の1問1答を解く（22問）','/games/quiz/?g=dom:10']]}};"""
    b = sub(b, re.compile(r"var D=\{.*?\}\};", re.S), lambda m: js_data)
    b = sub(b, """return '<a class="tl" href="#">'+x+'</a>'""", """return '<a class="tl" href="'+x[1]+'">'+x[0]+'</a>'""")
    b = sub(b, "out.innerHTML='<p class=\"rh\">'+d.t+'が苦手なら</p>",
            "out.innerHTML='<p class=\"rh\">'+d.t+'が苦手な人</p>")

    # 出典：本番の文（「過去問の本文は転載せず」は指示書7番で外す）
    b = sub(b, '<p class="src">情報確認日：2026-09-29</p>',
            '<p class="src">情報確認日：2026-09-29 ／ 出典：キャリアコンサルティング協議会「受験概要」「過去問題」（第30回・第31回・第32回 学科試験）。各問題のテーマだけをまとめています。</p>')

    # 次の一歩：勉強の道 STEP2
    for label, href in (("よく出る用語", "/hinshutsu/"), ("ことば図鑑（162語）", "/terms/"), ("理論家図鑑（66人）", "/theorists/")):
        b = sub(b, f'<a class="ncard" href="#"><span class="nn"><span class="x-step-tag">勉強の道 STEP2 ことばと理論</span></span><span class="tl">{label}</span></a>',
                f'<a class="ncard" href="{href}"><span class="nn"><span class="x-step-tag">勉強の道 STEP2 ことばと理論</span></span><span class="tl">{label}</span></a>')
    body, scripts = S.split_scripts(b)
    scripts = [s.replace("document.body.classList.add('js-on');", "document.body.classList.add('js-on');") for s in scripts]
    scripts += [f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
                f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
                f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>']
    body = body.replace("@@END@@", "@@END@@\n", 1) if not body.endswith("\n") else body
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("試験対策の記事", "/exam/#all"), ("学科試験の勉強法", None)]
    return finish(path, body.rstrip() + "\n", "02", crumb, extra_css=("shiken/02-plus.css",), scripts=scripts)


# =============================================================== 03 コラム
def build_03():
    path = "column/kimerarenai-yoru/index.html"
    r = P.rel_root(path)
    b = S.rough_body("03", path)
    # 頭：記事の型（小山に悩む人）。ラフの頭の文（連載名・h1・リード）はそのまま、夜の人の絵の枠（Canva の絵）は外す
    hero = re.search(r'<section class="x-chero x-uhero">.*?</section>', b, re.S).group(0)
    tags = re.search(r'<p class="tags">.*?</p>', hero, re.S).group(0)
    h1 = re.search(r"<h1>.*?</h1>", hero, re.S).group(0)
    lede = re.search(r'<p class="x-lede">.*?</p>', hero, re.S).group(0)
    names = re.search(r'<p class="x-names"[^>]*>.*?</p>', hero, re.S).group(0)
    meta = re.search(r'<p class="x-meta"[^>]*>.*?</p>', hero, re.S).group(0)
    new_hero = f"""<section class="hero1 x-col-hero"><div class="w">
  {tags.replace('<p class="tags">', '<p class="x-tagline tags">', 1)}
  {h1}
  <div class="hstage">
    <img class="garl" src="{r}img/kata/sora_garland.webp" alt="" aria-hidden="true">
    <img class="cld c1" src="{r}img/parts/01_sky_cloud_left.webp" alt="" aria-hidden="true">
    <img class="cld c2" src="{r}img/parts/03_sky_cloud_right.webp" alt="" aria-hidden="true">
    <p class="qb"><span class="lb">このページで答える悩み</span>協議会か、JCDAか。<br>ぜんぜん決まらない…<small>どっちを選んでも、論述が怖い</small></p>
    <div class="who1" aria-hidden="true">
      <span class="hm m1">？</span><span class="hm m2">？</span>
      <span class="mpic"><img class="hito" src="{r}img/kata/hito_3_yoru.webp" alt=""></span>
    </div>
    <img class="deco tent" src="{r}img/parts/t/13_blue_yellow_tent-136.webp" alt="" aria-hidden="true">
    <img class="deco fl1" src="{r}img/parts/t/23_flowers_left_group-180.webp" alt="" aria-hidden="true">
    <img class="deco fl2" src="{r}img/parts/t/25_flowers_right_group-180.webp" alt="" aria-hidden="true">
    <img class="deco bu1" src="{r}img/parts/t/24_bush_lower_left-136.webp" alt="" aria-hidden="true">
    <img class="deco bu2" src="{r}img/parts/t/26_bush_lower_right-136.webp" alt="" aria-hidden="true">
  </div>
  <i class="oka" aria-hidden="true"></i>
</div></section>"""
    b = b.replace(hero, new_hero, 1)
    # リード・団体の呼び名・更新日は、芝生の段（会話）の頭に
    b = sub(b, '<section class="x-talk sec2 green"><div class="x-col">',
            f'<section class="x-talk sec2 green"><div class="x-col">\n  <div class="x-lead">{lede}\n  {names}\n  {meta}</div>')
    # 正直な話・試験勉強にもどる・次に読むコラム：本番のリンク先
    b = sub(b, '<a class="tl" href="#">「やめたほうがいい人・向いている人」のページ（30秒の診断つき）</a>',
            '<a class="tl" href="/school-guides/merit-demerit/">「やめたほうがいい人・向いている人」のページ（30秒の診断つき）</a>')
    for label, href in (("積極的不確実性（ジェラット）", "/terms/positive-uncertainty/"), ("意思決定理論の系譜", "/terms/ishikettei-riron-keifu/"),
                        ("理論家図鑑：ジェラット", "/theorists/gelatt/"), ("試験の難易度と合格率", "/exam-guide/goukakuritsu/"),
                        ("論述ボードゲーム", "/games/ronjutsu/")):
        b = sub(b, f'<a href="#">{label}</a>', f'<a href="{href}">{label}</a>')
    for label, href in (("「どうせ無理」と言う日の、クランボルツ", "/column/guuzen-wo-mikata-ni/"), ("がんばれない時期の、ブリッジス", "/column/jinsei-no-chuuritsuken/"),
                        ("朝3時から起きているのに「自分の時間がない」", "/column/jibun-no-jikan-ga-nai/")):
        b = sub(b, f'<a class="ncard" href="#"><span class="nn">COLUMN</span><span class="tl">{label}</span></a>',
                f'<a class="ncard" href="{href}"><span class="nn">COLUMN</span><span class="tl">{label}</span></a>')
    b = sub(b, '<a class="tl" href="#">コラムの一覧（6本）</a>', '<a class="tl" href="/column/">コラムの一覧（6本）</a>')
    b = sub(b, '<p class="go"><a href="#">「どうせ無理」と言う日の、クランボルツ</a> →</p>',
            '<p class="go"><a href="/column/guuzen-wo-mikata-ni/">「どうせ無理」と言う日の、クランボルツ</a> →</p>')
    # 出口：面接練習会のページはまだないので、比較表の30秒しぼりこみ1つ（本番に # を出さない）
    b = sub(b, re.compile(r'<div class="in2">\s*<a class="x-ex" href="#">.*?</a>\s*', re.S), '<div class="in2 one">\n    ')
    body, scripts = S.split_scripts(b)
    scripts += [f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
                f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
                f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>']
    crumb = [("ホーム", "/"), ("試験対策", "/exam/"), ("コラム", "/column/"), ("COLUMN 06", None)]
    return finish(path, body.rstrip() + "\n", "03", crumb, extra_css=("shiken/03-plus.css",), scripts=scripts)


# =============================================================== 01 試験の入口
def build_01():
    path = "exam/index.html"
    r = P.rel_root(path)
    src = prod(path)
    soup = BeautifulSoup(src, "html.parser")
    b = S.rough_body("01", path)

    # 次の試験：本番にある「2027年3月7日」だけ（申込み・面接・合格発表の日は本番にないので出さない）
    b = sub(b, re.compile(r'<dl><dt>申込み</dt>.*?</dl>\s*<p class="sm"><a class="tl" href="#">試験の日程と、申込みのしかた</a></p>\s*', re.S), "")

    # 試験の全体像：本番の説明（リンクつき）を、くわしくの箱に
    zen = h2(soup, "試験の全体像").parent
    zen_ul = str(zen.find("ul"))
    zen_ps = "".join(str(p) for p in zen.find_all("p", recursive=False))
    b = sub(b, '<p class="src c">論述と面接（実技）は150点満点で90点以上。',
            f'<details class="more x-kuwa"><summary>試験の全体像を、くわしく</summary><div class="in">{zen_ul}{zen_ps}</div></details>\n  <p class="src c">論述と面接（実技）は150点満点で90点以上。')

    # 勉強の道：行き先を本番の住所に。STEP1 の「試験の日程（第34回）」は本番にページがないので「試験の難易度と合格率」に
    b = sub(b, '<li><a href="#">試験の日程（第34回）</a></li>', '<li><a href="#">試験の難易度と合格率</a></li>')
    for label, href in S.MICHI_ITEMS.items():
        b = b.replace(f'<a href="#">{label}</a>', f'<a href="{href}">{label}</a>')
        b = b.replace(f'<a class="tl" href="#">{label}</a>', f'<a class="tl" href="{href}">{label}</a>')
    # 前の地図（#map）・ぜんぶ（#all）・今日の3分（#daily）へ来るリンクの着地点も残す
    b = sub(b, '<section class="sec2 hb" id="michi"><div class="w">', '<section class="sec2 hb" id="michi"><div class="w"><span id="map" class="x-anchor"></span>')
    # 本番の「このサイトでの勉強のしかた」
    how = h2(soup, "このサイトでの勉強のしかた").find_next("ol")
    b = sub(b, re.compile(r'(<div class="x-last">.*?</div></div>)', re.S),
            lambda m: m.group(1) + f'\n  <details class="more x-kuwa nar0" style="max-width:744px;margin:24px auto 0"><summary>このサイトでの勉強のしかた</summary><div class="in">{str(how)}</div></details>')

    # 今日の3分学びタイム：本番のしくみ（js/daily.js・日ごとに変わる）をそのまま使う
    dg = soup.select_one(".daily-grid")
    cards = dg.select(".daily-card")
    labels = {"quiz": "今日の問題", "term": "今日の用語", "theorist": "今日の理論家"}
    dcs = []
    for c in cards:
        kind = c["data-daily"]
        lb = c.select_one(".daily-card__label")
        lb.string = labels.get(kind, lb.get_text())
        lb["class"] = ["daily-card__label", "lb"]
        c["class"] = (c.get("class") or []) + ["x-dc"]
        dcs.append(str(c))
    flow = '<ol class="x-flowtag" aria-label="今日の問題の流れ"><li class="on">選ぶ</li><li aria-hidden="true" class="ar">→</li><li>正誤</li><li aria-hidden="true" class="ar">→</li><li>解説</li><li aria-hidden="true" class="ar">→</li><li>次へ</li></ol>'
    dcs[0] = dcs[0].replace("</div>\n</div>", "</div>" + flow + "\n</div>") if "</div>\n</div>" in dcs[0] else re.sub(r"</div>\s*$", flow + "</div>", dcs[0])
    b = sub(b, re.compile(r'<div class="x-daily">.*?</div>\s*</div>\s*(?=<p class="c" style="margin:34px 0 0">)', re.S),
            '<div class="x-daily" id="daily">\n    ' + "\n    ".join(dcs) + "\n  </div>\n  ")
    b = sub(b, '<a class="cta" href="#">毎日1問1答にチャレンジ</a>', '<a class="cta" href="/games/quiz/" data-cta-type="daily-drill">毎日1問1答にチャレンジ</a>')
    b = sub(b, '今日の<b class="mark">問題・用語・理論家</b>、この3つだけ。今日のぶんだけで大丈夫。すきま3分で、ちゃんと前に進めるよ。',
            '今日の<b class="mark">問題・用語・理論家</b>、この3つだけ。今日のぶんだけで大丈夫。<b class="mark">すきま3分</b>で、ちゃんと前に進めるよ。')

    # 公式の過去問
    b = sub(b, '<a href="#"><b>キャリアコンサルティング協議会</b>', '<a href="https://www.career-shiken.org/about/learninfo/" rel="noopener nofollow" target="_blank"><b>キャリアコンサルティング協議会</b>')
    b = sub(b, '<a href="#"><b>日本キャリア開発協会（JCDA）</b>', '<a href="https://www.jcda-careerex.org/past/" rel="noopener nofollow" target="_blank"><b>日本キャリア開発協会（JCDA）</b>')

    # ひと休み：ゲームとコラム
    for label, href in (("理論家カードあわせ", "/games/match/"), ("理論家の流派仕分け", "/games/ryuha/"), ("理論の図あなうめ", "/games/anaume/"),
                        ("ミニゲームの一覧", "/games/"), ("「協議会か、JCDAか」で眠れない夜の、ジェラット", "/column/kimerarenai-yoru/"),
                        ("「どうせ無理」と言う日の、クランボルツ", "/column/guuzen-wo-mikata-ni/"), ("がんばれない時期の、ブリッジス", "/column/jinsei-no-chuuritsuken/"),
                        ("家族にイラッとした夜の、エリス", "/column/kazoku-genka-to-abc/"), ("コラムの一覧", "/column/")):
        b = sub(b, f'<li><a href="#">{label}</a></li>', f'<li><a href="{href}">{label}</a></li>')
    # 本番の「このテントで、あそびながら対策できるよ」（3つの道具と論述の型ノート）
    tent = h2(soup, "あそびながら対策できるよ").parent
    tools = tent.select_one(".exam-tools")
    for img in tools.select("img"):
        img.decompose()
    note = tent.select_one(".note-dl")
    for img in note.select("img"):
        img.decompose()
    tent_html = nowbr(str(tools) + str(note))
    # 「試験対策のページを、ぜんぶ見る」：本番の10の箱とリンクをそのまま
    cards = soup.select(".study-card")
    cols = []
    for c in cards:
        pid = c["aria-controls"]
        panel = soup.select_one("#" + pid)
        cols.append(f'<div><p>{c.select_one(".study-card__name").get_text()}<small>{c.select_one(".study-card__desc").get_text()}</small></p>'
                    f'{nowbr(str(panel.find("ul")))}</div>')
    allbox = (f'<details class="more x-all" id="all"><summary>試験対策のページを、ぜんぶ見る</summary><div class="in"><div class="cols">'
              + "".join(cols) + "</div></div></details>")
    b = sub(b, re.compile(r'<details class="more x-all">.*?</details>', re.S),
            lambda m: f'<details class="more x-kuwa x-tent"><summary>このテントで、あそびながら対策できるよ</summary><div class="in">{tent_html}</div></details>\n  ' + allbox)

    # 出口：面接練習会のページはまだないので、比較表の30秒しぼりこみ1つ
    b = sub(b, re.compile(r'<div class="in2">\s*<a class="x-ex" href="#">.*?</a>\s*', re.S), '<div class="in2 one">\n    ')

    # 動き：今日の問題のしかけ（ラフの見本用）は外し、本番の daily.js
    body, scripts = S.split_scripts(b)
    scripts = [re.sub(r"\n// 今日の問題：.*?\}\)\(\);", "", s, flags=re.S) for s in scripts]
    scripts += [f'<script src="{r}js/daily.js?v=v2026.0728.1616" defer></script>',
                f'<script src="{r}js/kata-shiken.js?v={S.CSS_VER}" defer></script>',
                f'<script src="{r}js/reveal.js?v=2026.1018b" defer></script>',
                f'<script src="{r}js/term-hints.js?v=v2026.1018" defer></script>']
    crumb = [("ホーム", "/"), ("試験対策", None)]
    out = finish(path, body.rstrip() + "\n", "01", crumb, extra_css=("shiken/01-plus.css",), scripts=scripts)
    return out


if __name__ == "__main__":
    pass  # 絵と共通の CSS は ippen_shiken.py の prepare（親の道具）で用意ずみ
    for n in sys.argv[1:] or ("01", "02", "03"):
        {"01": build_01, "02": build_02, "03": build_03}[n]()
