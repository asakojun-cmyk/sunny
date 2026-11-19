#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：ラフ（新しい型の見本）から本番のページを組む道具。

ラフの body（ヒーロー〜ピクニックの絵〜次の段）をそのまま使い、
- 頭（計測・title・説明文・canonical・OGP・アイコン）は本番のページから引きつぐ（新しいページは指定の文で作る）
- 構造化データ・ページの中の <style> はラフのもの（見える中身と同じ言葉にするため）
- ヘッダー・道しるべ・パンくず・フッター・下のメニューは scripts/ippen_parts.py の共通の部品
- 絵の住所は img/kata/・img/parts/ の webp に、ラフどうしのリンクは本番の住所に
- ラフの印（rtag）・「このラフを使う本番のページ」の段・作業メモのコメントは外す

使い方: python3 scripts/ippen_from_rough.py <ページの名前> …（名前は下の PAGES）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402

ROOT = P.ROOT
ROUGH = "/Users/iwawakiasako/Documents/Obsidian Vault/GitHub/picnic-docs/1108_サイトの設計/イメージ/ラフ_1117"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500&family=Zen+Kaku+Gothic+New:wght@500;700&family=Zen+Kurenaido&display=swap" rel="stylesheet">')

ANALYTICS = """<!-- 表示を速くするため、アクセス解析(Googleアナリティクス・Clarity)は、最初のタップ・スクロール、または表示の3.5秒後に読む -->
<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-09GCDPKMKD');
(function(w,d){var done=false;function go(){if(done)return;done=true;try{if(localStorage.getItem("cp-notrack")==="1")return}catch(e){}
var g=d.createElement("script");g.async=true;g.src="https://www.googletagmanager.com/gtag/js?id=G-09GCDPKMKD";d.head.appendChild(g);
w.clarity=w.clarity||function(){(w.clarity.q=w.clarity.q||[]).push(arguments)};var c=d.createElement("script");c.async=true;c.src="https://www.clarity.ms/tag/yxefgkb9kq";d.head.appendChild(c);}
["pointerdown","keydown","scroll","touchstart"].forEach(function(e){w.addEventListener(e,go,{once:true,passive:true})});
function later(){setTimeout(go,3500)}if(d.readyState==="complete")later();else w.addEventListener("load",later);})(window,document);
</script>"""

# ラフの絵 → 本番の絵（ページの場所からの相対にする前の、サイトの上からの住所）
IMG = [
    (r'\.\./1115_Canvaの絵入り_素材/sunny_下の光を足した\.png', "img/kata/sunny.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/sora_garland\.png', "img/kata/sora_garland.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/hero_スーパーさんのピクニック_空を透明に\.png', "img/kata/hero_picnic.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/hito_(\d_[a-z]+)(?:_fuchi)?\.png', r"img/kata/hito_\1.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/hito_profile\.png', "img/kata/hito_profile.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/(school_[a-z]+)\.png', r"img/kata/\1.webp"),
    (r'\.\./1115_Canvaの絵入り_素材/gara_kimete\.png', "img/kata/gara_kimete.webp"),
    (r'file:///Users/iwawakiasako/Projects/sunny/img/parts/([^"\']+?)\.(?:png|webp)', r"img/parts/\1.webp"),
    (r'(?<=["\'(])img/05_pinwheel-64\.webp', "img/parts/t/05_pinwheel-64.webp"),
]

# 1ページずつの決めごと
PAGES = {
    "lec": dict(
        rough="02_学校ページ.html", out="schools/lec/index.html", head_from="schools/lec/index.html",
        crumb=[("ホーム", "/"), ("講座をえらぶ", "/schools/"), ("LEC東京リーガルマインド", None)],
        links={
            "01_比較表.html#tool": "/schools/compare/#tool",
            "01_比較表.html": "/schools/compare/",
            "03_ガイド記事.html": "/school-guides/kyufukin-tetsuzuki/",
            'class="tl" href="index.html"': 'class="tl" href="/#boshu"',
        },
        fix=[
            # 説明会の予約先：いまの学校ページと同じ紹介リンク（A8・計測の画像つき）
            ('<p class="ctaw"><a class="cta" href="#">LECの説明会の予約先</a></p>',
             '<p class="ctaw"><a class="cta" data-ev="school_cta_lec" href="https://px.a8.net/svt/ejp?a8mat=4BCMO3+2VLGT6+1G62+BW8O2&amp;a8ejpredirect=https%3A%2F%2Fwww.lec-jp.com%2Fcaricon%2Fevent%2Fguidance%2F" rel="sponsored noopener noreferrer" target="_blank">LECの説明会の予約先</a><img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BCMO3+2VLGT6+1G62+BW8O2" alt="" style="position:absolute" loading="lazy" decoding="async"></p>'),
            ('<a class="ncard" href="#"><span class="nn">選ぶ前に決めておく</span>', '<a class="ncard" href="/school-guides/how-to-choose/"><span class="nn">選ぶ前に決めておく</span>'),
            ('<section class="hero1 x-uhero">', '<section class="hero1">'),
        ],
    ),
    "kyufukin-tetsuzuki": dict(
        rough="03_ガイド記事.html", out="school-guides/kyufukin-tetsuzuki/index.html", head_from=None,
        title="キャリアコンサルタントの給付金の手続き・申請はいつまで？ハローワークでの流れ｜キャリコン学びピクニック",
        crumb=[("ホーム", "/"), ("費用と給付金", "/school-guides/kyufukin/"), ("給付金の手続き", None)],
        links={
            "01_比較表.html#tool": "/schools/compare/#tool",
            "01_比較表.html": "/schools/compare/",
            "03_ガイド記事.html": "/school-guides/kyufukin-tetsuzuki/",
            'href="index.html"': 'href="/"',
        },
        fix=[
            # 給付金のアニメ（トップの写し・150KB）は入れない。すぐ下の3段の表に同じ中身がある
            (re.compile(r'\s*<div class="anim-wrap"><iframe[^>]*></iframe></div>'), ""),
            ('<a class="ncard" href="#"><span class="nn">いくら戻るか知る</span>', '<a class="ncard" href="/school-guides/kyufukin/"><span class="nn">いくら戻るか知る</span>'),
            ('<a class="ncard" href="#"><span class="nn">ほかのお金も知る</span>', '<a class="ncard" href="/shikaku-guide/#hiyou"><span class="nn">ほかのお金も知る</span>'),
        ],
    ),
}


# スマホ（〜420px）で h1 の1行目（学校名など・折り返さない）が右にはみ出さないように
H1_SP = ('<style id="ippen-h1">@media (max-width:420px){body.kata .hero1 h1{font-size:21px;letter-spacing:.06em}}'
         '</style>')


def rel(path, site_path):
    return P.rel_root(path) + site_path


def head_from_prod(prod_html):
    """本番のページの頭から、計測〜アイコンまで（古い CSS・構造化データ・字の指定は持ってこない）"""
    h = prod_html.split("</head>", 1)[0]
    keep = []
    for pat in (r'<meta name="viewport"[^>]*>', r"<title>.*?</title>", r'<meta name="description"[^>]*>',
                r'<link rel="canonical"[^>]*>', r'<meta property="og:[^"]+"[^>]*>', r'<meta name="twitter:[^"]+"[^>]*>',
                r'<link rel="icon"[^>]*>', r'<link rel="apple-touch-icon"[^>]*>'):
        keep += re.findall(pat, h, re.S)
    return "\n".join(keep)


def new_head(path, cfg, rough_head):
    desc = re.search(r'<meta name="description" content="([^"]*)"', rough_head).group(1)
    url = "https://carepicnic.com" + P.url_of(path)
    t = cfg["title"]
    r = P.rel_root(path)
    return "\n".join([
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{t}</title>", f'<meta name="description" content="{desc}">', f'<link rel="canonical" href="{url}">',
        '<meta property="og:site_name" content="キャリコン学びピクニック">', f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{desc}">', '<meta property="og:type" content="article">',
        f'<meta property="og:url" content="{url}">', '<meta property="og:locale" content="ja_JP">',
        '<meta property="og:image" content="https://carepicnic.com/img/ogp.png">',
        '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:image" content="https://carepicnic.com/img/ogp.png">',
        f'<link rel="icon" type="image/png" href="{r}img/favicon.png">', f'<link rel="apple-touch-icon" href="{r}img/sunny-icon.png">',
    ])


def build(name_or_cfg):
    """name（PAGES の名前）か、同じ形の dict を渡す。dict なら rough（ラフ_1117 の中の名前）の
    かわりに rough_path（絶対パス）か rough_html（中身）でもよい"""
    cfg = PAGES[name_or_cfg] if isinstance(name_or_cfg, str) else name_or_cfg
    path = cfg["out"]
    if cfg.get("rough_html"):
        src = cfg["rough_html"]
    else:
        src = open(cfg.get("rough_path") or os.path.join(ROUGH, cfg["rough"]), encoding="utf-8").read()
    rhead, rbody = src.split("</head>", 1)
    # 頭
    if cfg.get("head_from"):
        meta = head_from_prod(open(os.path.join(ROOT, cfg["head_from"]), encoding="utf-8").read())
    else:
        meta = new_head(path, cfg, rhead)
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', rhead, re.S)
    styles = re.findall(r"<style\b.*?</style>", rhead, re.S)
    # パンくずの構造化データ：住所のない段に住所を入れる
    crumbs = cfg["crumb"]
    fixed_ld = []
    for j in ld:
        if '"BreadcrumbList"' in j:
            items = ",".join(
                '{"@type": "ListItem", "position": %d, "name": "%s"%s}' % (
                    i + 1, n, ', "item": "https://carepicnic.com%s"' % (h if h else P.url_of(path)))
                for i, (n, h) in enumerate(crumbs))
            j = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BreadcrumbList", '
                 f'"itemListElement": [{items}]}}</script>')
        fixed_ld.append(j)
    head = "\n".join([
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">', ANALYTICS, meta, FONTS,
        f'<link rel="stylesheet" href="{P.rel_root(path)}css/kata.css?v=2026.1120">',
        *fixed_ld, *styles, H1_SP, P.css_link(path), "</head>",
    ])
    # 本文：ラフの印・ラフの部品を外す
    body = rbody
    body = re.sub(r'<div class="rtag">.*?</div></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<header class="hd">.*?</header>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="way".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="w"><p class="crumb">.*?</p></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<footer class="ft">.*?</footer>\s*', "@@END@@\n", body, count=1, flags=re.S)
    body = re.sub(r'<section class="pages".*?</section>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="bn".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r"\n?<!--.*?-->", "", body, flags=re.S)
    # 絵の住所
    for a, b in IMG:
        body = re.sub(a, lambda m, b=b: rel(path, m.expand(b)), body)
    # ラフどうしのリンク
    for a, b in cfg.get("links", {}).items():
        body = body.replace(f'href="{a}"', f'href="{b}"') if not a.startswith(("class=", "href=")) else body.replace(a, b)
    # 一番下の「次の段」（学校えらびの側はどのページも同じ行き先）
    body = body.replace('<a href="#">入学が決まったら、試験までの勉強の道へ</a>', '<a href="/start/">入学が決まったら、試験までの勉強の道へ</a>')
    body = body.replace('<a class="tl" href="#">キャリコンへの道を、ぜんぶ見る</a>', '<a class="tl" href="#sitemap">キャリコンへの道を、ぜんぶ見る</a>')
    body = body.replace('<p class="back"><a href="#">← 前の段「知る」にもどる</a></p>', '<p class="back"><a href="/careers/">← 前の段「知る」にもどる</a></p>')
    for a, b in cfg.get("fix", []):
        body = a.sub(b, body) if hasattr(a, "sub") else body.replace(a, b)
    # 共通の部品
    top = P.top_parts(path, P.crumb_html(crumbs))
    body = re.sub(r"(<body[^>]*>\s*<svg.*?</svg>\s*)", lambda m: m.group(1) + top + "\n", body, count=1, flags=re.S)
    body = body.replace("@@END@@\n", P.end_parts(path))
    out = head + body
    os.makedirs(os.path.dirname(os.path.join(ROOT, path)), exist_ok=True)
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as fh:
        fh.write(out)
    # 確かめ
    bad = [x for x in ("file://", "1115_Canvaの絵入り_素材", "ラフ", ".png\"", 'href="#"', "common.css") if x in out]
    print(f"{path}: {len(out)//1024}KB  気になる文字: {bad or 'なし'}")


if __name__ == "__main__":
    for n in sys.argv[1:] or PAGES:
        build(n)
