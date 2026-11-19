#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：全ページ共通の部品を1か所で作り、全ページに入れる道具。

部品：ヘッダー（.hd）・キャリコンへの道（.way）・パンくず（.kc .crumb）・フッター（.ft・地図つき）・
スマホの下のメニュー（.bn）。見た目は css/kyoutsu.css。
- 下のメニューのまん中（11/19 ちゃん決定 A）：学校えらびの側＝「費用」、試験の側＝「今日の問題」
- 各ページの本文（<main> の中・授業の音声が読む class）はさわらない。パンくずだけ <main> の外へ出す
- トップ（index.html）は手で組んだ部品のまま（さわらない）

使い方
  python3 scripts/ippen_parts.py            … 全ページに入れる（変えたページの数を出す）
  python3 scripts/ippen_parts.py --dry      … 書きかえずに数だけ
ほかの道具からは import して header_html(path) などを使う（新しい型のページを組む道具）。
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_VER = "2026.1120"

SKIP = {
    "index.html",                      # トップは手で組んだ部品
    "school-experience/index.html",    # 転送だけ
    "terms/helping-carkhuff/index.html",  # 転送だけ
}
SKIP_PREFIX = ("_to_delete/", "notrack/", "node_modules/", ".git/")

EXAM_PREFIX = ("exam/", "exam-guide/", "start/", "column/", "terms/", "theorists/", "games/",
               "obento/", "hinshutsu/", "kakomon-keiko/", "laws/", "diagrams/", "text/", "books/",
               "omamori/", "search/")
SITE_PAGES = ("about/", "contact/", "privacy/", "404.html")

NAV = [("キャリコンとは", "/careers/"), ("講座をえらぶ", "/schools/"),
       ("費用と給付金", "/school-guides/kyufukin/"), ("試験対策", "/exam/"),
       ("受かったあと", "/shikaku-guide/#touroku")]
WAY = [(1, "知る", "/careers/"), (2, "学校選び", "/schools/compare/"), (3, "試験対策", "/exam/"),
       (4, "登録", "/shikaku-guide/#touroku"), (5, "はじめの<wbr>一歩", None),
       (6, "稼ぐ", "/school-guides/zaitaku-fukugyo/")]

# 下のメニュー（端の2つと「さがす」は全ページ同じ。2つめとまん中が側ごとにちがう）
BN_SCHOOL = [("nav_home", "/", "⌂", "ホーム"), ("nav_compare", "/schools/compare/", "☰", "6校くらべ"),
             ("nav_cost", "/school-guides/kyufukin/", "¥", "費用"), ("nav_search", "/search/", "⌕", "さがす"),
             ("nav_menu", "#sitemap", "≡", "メニュー")]
BN_EXAM = [("nav_home", "/", "⌂", "ホーム"), ("nav_michi", "/start/", "⋯", "勉強の道"),
           ("nav_daily", "/exam-guide/last-30days/#mainichi", "?", "今日の問題"),
           ("nav_search", "/search/", "⌕", "さがす"), ("nav_menu", "#sitemap", "≡", "メニュー")]

FOOTER_MAP = """<nav class="map" aria-label="サイト全体のメニュー">
    <div><h4><i>1</i>知る</h4><ul><li><a href="/shikaku-guide/gimon/">キャリコンって何？（よくある質問40問）</a></li><li><a href="/careers/">キャリアコンサルタントの仕事</a></li><li><a href="/shikaku-guide/">資格まるわかりガイド（とり方・期間）</a></li><li><a href="/exam-guide/goukakuritsu/">試験の難易度と合格率</a></li><li><a href="/school-guides/merit-demerit/">やめたほうがいい人・向いている人</a></li></ul></div>
    <div><h4><i>2</i>学校選び</h4><ul><li><a href="/schools/compare/">6校の比較表</a></li><li><a href="/schools/compare/#apply-h">6校の無料説明会の申込み先</a></li><li><a href="/#school-match">いまのあなたに合う学校をしぼる</a></li><li><a href="/schools/">養成学校一覧</a></li><li><a href="/school-guides/kyufukin/">費用と給付金</a></li><li><a href="/school-guides/kyufukin-tetsuzuki/">給付金の手続き（いつまでに・何を）</a></li><li><a href="/school-guides/how-to-choose/">養成学校の選び方</a></li><li><a href="/school-guides/online/">オンライン講座の選び方</a></li><li><a href="/school-guides/working-mothers/">子育て中の学校選び</a></li><li><a href="/school-guides/training-and-exam-preparation/">養成講習と試験対策講座の違い</a></li><li><a href="/school-reviews/chiiki-renkei-platform/">運営者の受講体験記</a></li><li><a href="/schools/chiiki-renkei-platform/#kai">運営者が出た説明会の話</a></li></ul></div>
    <div><h4><i>3</i>試験対策</h4><ul><li><a href="/exam/">試験対策トップ（学科・論述・面接）</a></li><li><a href="/start/">初学者の学習ルート</a></li><li><a href="/terms/">キャリコンことば図鑑</a></li><li><a href="/theorists/">理論家図鑑</a></li><li><a href="/laws/">労働法・統計・制度</a></li><li><a href="/games/quiz/">1問1答ドリル</a></li><li><a href="/games/">3分ミニゲーム</a></li><li><a href="/diagrams/">図解ライブラリ</a></li><li><a href="/text/">学科 直前対策テキスト（PDF）</a></li><li><a href="/books/">さらに学べる本棚</a></li><li><a href="/omamori/">お守りページ</a></li></ul></div>
    <div><h4><i>4</i>登録・その先</h4><ul><li><a href="/shikaku-guide/#touroku">受かったあとの登録</a></li><li><a href="/school-guides/zaitaku-fukugyo/">在宅・副業で働く</a></li></ul><h4>このサイトのこと</h4><ul><li><a href="/">ホーム</a></li><li><a href="/search/">サイト内検索</a></li><li><a href="/column/">コラム</a></li><li><a href="/about/">このサイトについて</a></li><li><a href="/contact/">お問い合わせ</a></li><li><a href="/privacy/">プライバシーポリシー・免責事項</a></li></ul></div>
  </nav>"""

FOOTER = """<footer class="ft" id="sitemap"><div class="w">
  {map}
  <div class="cols">
    <div><h4>紹介料のこと</h4><p>紹介料をいただいているのは、<span class="pr">PR</span>の表示がある学校です。あなたの受講料は変わりません。6校とも同じ項目・同じ確かめ方（公式ページ・確かめた日つき）で載せています。</p></div>
    <div><h4>ご注意</h4><p>掲載している学校の料金・日程・給付金などの情報は変更される可能性があります。申込み前に必ず各校の公式サイトで最新情報をご確認ください。</p><p>法律・統計・試験制度に関する記述は、一次資料で確認できた範囲で掲載しています。</p></div>
  </div>
  <p class="copy">運営者：岩脇 朝子　&copy; 2026 キャリコン学びピクニック</p>
</div></footer>""".replace("{map}", FOOTER_MAP)


def rel_root(path):
    """ページの場所から、サイトのいちばん上までの相対パス（絵の住所に使う）"""
    depth = path.count("/")
    return "../" * depth if depth else ""


def url_of(path):
    u = "/" + path
    return u[:-len("index.html")] if u.endswith("index.html") else u


def side(path):
    if path.startswith(EXAM_PREFIX) or path == "exam-room.html":
        return "exam"
    if path.startswith(SITE_PAGES):
        return "site"
    return "school"


def way_step(path):
    s = side(path)
    if s == "exam":
        return 3
    if s == "site":
        return None
    if path.startswith(("careers/", "shikaku-guide/", "school-guides/merit-demerit/")):
        return 1
    if path.startswith("school-guides/zaitaku-fukugyo/"):
        return 6
    return 2


def nav_on(path):
    s = side(path)
    if s == "exam":
        return "/exam/"
    if s == "site":
        return None
    if path.startswith(("careers/", "shikaku-guide/gimon/")) or path == "shikaku-guide/index.html":
        return "/careers/"
    if path.startswith(("school-guides/kyufukin", "school-guides/yasui/")):
        return "/school-guides/kyufukin/"
    if path.startswith("school-guides/zaitaku-fukugyo/"):
        return "/shikaku-guide/#touroku"
    return "/schools/"


def header_html(path):
    r = rel_root(path)
    on = nav_on(path)
    links = "".join(f'<a href="{h}"{" class=\"on\"" if h == on else ""}>{t}</a>' for t, h in NAV)
    return (f'<header class="hd"><div class="w"><a class="logo" href="/"><img src="{r}img/kata/sunny.webp" alt="">'
            f'キャリコン学びピクニック</a><nav class="nav" aria-label="メニュー">{links}</nav></div></header>')


def way_html(path):
    st = way_step(path)
    lis = []
    for n, t, h in WAY:
        a = f'<a href="{h}">' if h else "<a>"
        if n == st:
            lis.append(f'<li class="on">{a}<i>{n}</i>{t}<small>いまここ</small></a></li>')
        else:
            lis.append(f"<li>{a}<i>{n}</i>{t}</a></li>")
    return ('<nav class="way" aria-label="キャリコンへの道（6つの段）"><div class="w"><p class="wl">キャリコンへの道<br>6つの段</p>'
            f'<ol>{"".join(lis)}</ol></div></nav>')


def crumb_html(items):
    """items = [(名前, 住所かNone)]"""
    out = []
    for i, (name, href) in enumerate(items):
        if href and i < len(items) - 1:
            out.append(f'<a href="{href}">{name}</a>')
        else:
            out.append(name)
    return f'<div class="kc"><p class="crumb">{" › ".join(out)}</p></div>'


def bn_html(path):
    items = BN_EXAM if side(path) == "exam" else BN_SCHOOL
    here = url_of(path)
    out = []
    for ev, href, ic, label in items:
        on = ' class="on"' if href == here else ""
        mid = " data-bn-mid" if ev in ("nav_cost", "nav_daily") else ""
        out.append(f'<a href="{href}" data-ev="{ev}"{mid}><span{on}><i>{ic}</i>{label}</span></a>')
    return f'<nav class="bn" aria-label="下のメニュー">{"".join(out)}</nav>'


def footer_html(path=None):
    return FOOTER


def css_link(path):
    return f'<link rel="stylesheet" href="{rel_root(path)}css/kyoutsu.css?v={CSS_VER}">'


# ---- 古いページのパンくず（<nav class="breadcrumbs">）を、新しい形に写す ----
BC = re.compile(r'<nav class="breadcrumbs"[^>]*>(.*?)</nav>\s*', re.S)
LI = re.compile(r"<li[^>]*>(.*?)</li>", re.S)
A = re.compile(r'<a [^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.S)


def abs_href(path, href):
    if href.startswith(("http", "/", "#")):
        return href
    base = "/" + os.path.dirname(path)
    p = os.path.normpath(os.path.join(base, href))
    if href.endswith("/") or href in ("..", "../..", "../../.."):
        p = p.rstrip("/") + "/"
    p = p.replace("index.html", "")
    return p if p else "/"


def old_crumb_items(path, inner):
    items = []
    for li in LI.findall(inner):
        m = A.search(li)
        if m:
            items.append((re.sub(r"<[^>]+>", "", m.group(2)).strip(), abs_href(path, m.group(1))))
        else:
            items.append((re.sub(r"<[^>]+>", "", li).strip(), None))
    return items


OLD_HEADER = re.compile(r'<header class="site-header">.*?</header>\s*', re.S)
OLD_FOOTER = re.compile(r'<footer class="site-footer"[^>]*>.*?</footer>\s*', re.S)
OLD_BN = re.compile(r'<nav class="bottom-nav".*?</nav>\s*', re.S)
NEW_HEADER = re.compile(r'<header class="hd">.*?</header>\s*', re.S)
NEW_WAY = re.compile(r'<nav class="way".*?</nav>\s*', re.S)
NEW_FOOTER = re.compile(r'<footer class="ft"[^>]*>.*?</footer>\s*', re.S)
NEW_BN = re.compile(r'<nav class="bn".*?</nav>\s*', re.S)
NEW_CRUMB_KATA = re.compile(r'<div class="w"><p class="crumb">(.*?)</p></div>\s*', re.S)
NEW_CRUMB = re.compile(r'<div class="kc"><p class="crumb">.*?</p></div>\s*', re.S)
BODY_OPEN = re.compile(r"<body[^>]*>\s*(?:<a class=\"skip-link\"[^>]*>[^<]*</a>\s*)?", re.S)


def top_parts(path, crumb):
    parts = [header_html(path)]
    if path != "exam-room.html":
        parts.append(way_html(path))
    if crumb:
        parts.append(crumb)
    return "\n".join(parts) + "\n"


def end_parts(path):
    return footer_html(path) + "\n" + bn_html(path) + "\n"


def apply(path, s):
    """1ページ分。新しい文字列を返す"""
    crumb = ""
    m = BC.search(s)
    if m:
        # 古いページは <main> の中のその場所で入れかえる（授業の音声が次のページへ移るとき、
        # lesson-player.js は <main> の中だけを入れかえるので、外に出すとパンくずが前の言葉のまま残る）
        s = s[:m.start()] + crumb_html(old_crumb_items(path, m.group(1))) + "\n" + s[m.end():]
    elif "<main" not in s:
        m = NEW_CRUMB.search(s)
        if m:
            crumb = m.group(0).strip()
            s = s[:m.start()] + s[m.end():]
        else:
            m = NEW_CRUMB_KATA.search(s)
            if m:
                crumb = f'<div class="kc"><p class="crumb">{m.group(1)}</p></div>'
                s = s[:m.start()] + s[m.end():]
    top = top_parts(path, crumb)
    # 上の部品：古い・新しいヘッダーを外して、同じ場所に入れる
    m = OLD_HEADER.search(s) or NEW_HEADER.search(s)
    if m:
        s = s[:m.start()] + "@@TOP@@" + s[m.end():]
        s = NEW_WAY.sub("", s, count=1)
        s = s.replace("@@TOP@@", top, 1)
    else:
        b = BODY_OPEN.search(s)
        s = s[:b.end()] + top + s[b.end():]
    # 下の部品：いまのフッターの場所に、フッター＋下のメニューを入れる
    for rx in (OLD_BN, NEW_BN):
        s = rx.sub("", s, count=1)
    m = OLD_FOOTER.search(s) or NEW_FOOTER.search(s)
    if m:
        s = s[:m.start()] + end_parts(path) + s[m.end():]
    else:
        # フッターのないページ：最後の <script> のまとまりの前（なければ </body> の前）
        i = s.rfind("</body>")
        tail = s[:i]
        mm = re.search(r"(?:\s*<script\b[^>]*>(?:(?!</script>).)*</script>)+\s*$", tail, re.S)
        j = mm.start() if mm else len(tail)
        s = tail[:j].rstrip() + "\n" + end_parts(path) + tail[j:].lstrip("\n") + s[i:]
    # 見た目の CSS（</head> の直前に1本）
    if "css/kyoutsu.css" not in s:
        s = s.replace("</head>", css_link(path) + "\n</head>", 1)
    return s


def pages():
    os.chdir(ROOT)
    for f in sorted(glob.glob("**/*.html", recursive=True)):
        if f in SKIP or f.startswith(SKIP_PREFIX):
            continue
        yield f


def main():
    dry = "--dry" in sys.argv
    changed = 0
    kinds = {}
    for f in pages():
        with open(f, encoding="utf-8") as fh:
            s = fh.read()
        new = apply(f, s)
        k = side(f)
        kinds[k] = kinds.get(k, 0) + 1
        if new != s:
            changed += 1
            if not dry:
                with open(f, "w", encoding="utf-8") as fh:
                    fh.write(new)
    print(f"pages: {sum(kinds.values())} {kinds} changed: {changed}{' (dry)' if dry else ''}")


if __name__ == "__main__":
    main()
