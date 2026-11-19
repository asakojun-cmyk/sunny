#!/usr/bin/env python3
"""いっぺんの入れかえ（2026-11-20）：試験の側のページを、ラフ_1119（新しい型の見本）で組むための共通の道具。

カテゴリごとの道具（scripts/ippen_shiken_<名前>.py）がこれを import して使う。
- 頭：本番のページの計測・title・説明文・canonical・OGP・アイコン・構造化データをそのまま引きつぐ
- 見た目：kata.css ＋ css/kata-shiken.css（12枚の tooitsu-1119 と kyoutsu-buhin を1本に）＋ css/shiken/<型>.css（ラフのページの CSS）
- 上と下の部品：scripts/ippen_parts.py（ヘッダー・道しるべ・パンくず・フッター・下のメニュー）
- 絵の住所：img/kata/・img/parts/・img/nigaoe/（理論家の似顔絵）
- ページの中身（パンくず〜一番下の帯）は <main id="main"> の中に入れる。
  授業の音声（js/lesson-player.js）は次の言葉へ進むとき <main> の中だけを入れかえるため。

使い方（ほかの道具から）
  import ippen_shiken as S
  S.prepare()                      … 絵と共通の CSS を用意する（何度回しても同じ）
  rough = S.rough_body("04")       … ラフの本文（部品・ラフの印を外し、絵とリンクを本番の住所に）
  html = S.page(path, prod_html, body, cat="04", crumb=[...], extra_css=[...], scripts=[...])
"""
import glob
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402

ROOT = P.ROOT
IMAGE = "/Users/iwawakiasako/Documents/Obsidian Vault/GitHub/picnic-docs/1108_サイトの設計/イメージ"
ROUGH = IMAGE + "/ラフ_1119_試験の側"
NIGAOE = IMAGE + "/1119_理論家の似顔絵_web"
CSS_VER = "2026.1120s"

ROUGH_FILES = {
    "01": "1119_ラフ_01_試験の入口.html", "02": "1119_ラフ_02_試験対策の記事.html", "03": "1119_ラフ_03_コラム.html",
    "04": "1119_ラフ_04_ことば図鑑.html", "04b": "1119_ラフ_04b_ことば図鑑_一覧.html", "05": "1119_ラフ_05_理論家図鑑.html",
    "05b": "1119_ラフ_05b_理論家図鑑_一覧と系譜.html", "06": "1119_ラフ_06_一問一答.html", "07": "1119_ラフ_07_論述.html",
    "08": "1119_ラフ_08_ミニゲーム.html", "09": "1119_ラフ_09_お弁当.html", "10": "1119_ラフ_10_試験の道具.html",
}
# ラフどうしのリンク → 本番の住所
ROUGH_URL = {
    "01": "/exam/", "02": "/exam-guide/gakka-benkyoho/", "03": "/column/kimerarenai-yoru/", "04": "/terms/supervision/",
    "04b": "/terms/", "05": "/theorists/rogers/", "05b": "/theorists/", "06": "/games/quiz/", "07": "/games/ronjutsu/",
    "08": "/games/", "09": "/obento/rogers/", "10": "/hinshutsu/",
}
# 勉強の道（01 試験の入口が正本）。カテゴリごとの STEP は各道具が決める
MICHI = "/exam/#michi"


# ---------------------------------------------------------------- 絵と CSS
def prepare():
    """移動図書館の絵（webp）・理論家の似顔絵・共通の CSS を用意する"""
    from PIL import Image
    kata = os.path.join(ROOT, "img/kata")
    dst = os.path.join(kata, "hero_library.webp")
    src = IMAGE + "/1115_Canvaの絵入り_素材/hero_移動図書館_空を透明に.png"
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGBA")
        if im.width > 1800:
            im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=82, method=6)
    nd = os.path.join(ROOT, "img/nigaoe")
    os.makedirs(nd, exist_ok=True)
    for f in glob.glob(NIGAOE + "/*.webp"):
        b = os.path.basename(f)
        if b.startswith("_"):
            continue
        t = os.path.join(nd, b)
        if not os.path.exists(t) or os.path.getsize(t) != os.path.getsize(f):
            shutil.copyfile(f, t)
    write_common_css()


def _rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, depth, start = [], 0, 0
    for j, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(re.sub(r"\s+", " ", css[start:j + 1]).strip())
                start = j + 1
    return out


def fix_urls(s, r):
    """ラフの中の絵の住所を、本番の住所（r＝サイトのいちばん上までの相対）にする"""
    s = s.replace("../1115_Canvaの絵入り_素材/hero_移動図書館_空を透明に.png", r + "img/kata/hero_library.webp")
    s = s.replace("../1115_Canvaの絵入り_素材/gara_kimete.png", r + "img/kata/gara_kimete.webp")
    s = re.sub(r"\.\./1119_理論家の似顔絵_web/([a-z0-9_-]+\.webp)", lambda m: r + "img/nigaoe/" + m.group(1), s)
    s = re.sub(r"(?:\.\./)+Projects/sunny(?:-rough1117-dan1)?/img/", r + "img/", s)
    s = s.replace("img/parts/../", "img/")
    return s


def write_common_css():
    """12枚の tooitsu-1119・kyoutsu-buhin を1本に（同じ規則は1回だけ・ラフの順）。
    ほかに、ラフの1枚目の <style>（カテゴリの見た目）を css/shiken/<型>.css に書く"""
    seen, rules = set(), []
    os.makedirs(os.path.join(ROOT, "css/shiken"), exist_ok=True)
    for cat, fn in ROUGH_FILES.items():
        s = open(os.path.join(ROUGH, fn), encoding="utf-8").read()
        head = s.split("</head>", 1)[0]
        for sid in ("kyoutsu-buhin", "tooitsu-1119", "nigaoe-1119", "chuuou-1119"):
            m = re.search(r'<style id="%s">(.*?)</style>' % sid, head, re.S)
            if not m:
                continue
            for rule in _rules(m.group(1)):
                if rule not in seen:
                    seen.add(rule)
                    rules.append(rule)
        first = re.search(r"<style>(.*?)</style>", head, re.S)
        cat_css = fix_urls(first.group(1), "../../")
        with open(os.path.join(ROOT, f"css/shiken/{cat}.css"), "w", encoding="utf-8") as fh:
            fh.write(f"/* 試験の側 {cat}（{fn} の見た目）。scripts/ippen_shiken.py が書く。直すときはラフを直してから回す */\n")
            fh.write(cat_css.strip() + "\n")
    css = "\n".join(rules)
    css = fix_urls(css, "../")
    with open(os.path.join(ROOT, "css/kata-shiken.css"), "w", encoding="utf-8") as fh:
        fh.write("/* 試験の側の共通（ラフ_1119 の12枚の tooitsu-1119・kyoutsu-buhin などを1本に）。"
                 "scripts/ippen_shiken.py が書く。足す規則は css/kata-shiken-plus.css へ */\n")
        fh.write(css + "\n")


# ---------------------------------------------------------------- 本番のもとのページ
BASE = "ac71b1714"  # 試験の側を組みかえる前（共通の部品だけ入った版）。何度回しても同じものから組む


def prod_html(path):
    import subprocess
    return subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:{path}"], capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- ラフの本文
def rough_html(cat):
    return open(os.path.join(ROUGH, ROUGH_FILES[cat]), encoding="utf-8").read()


def rough_body(cat, path):
    """ラフの <body> の中身。ラフの印・上と下の部品・作業メモ・確かめ用のしかけを外し、絵とリンクを本番の住所に。
    上の部品の場所に @@TOP@@、フッターの場所に @@END@@ を置く"""
    s = rough_html(cat)
    body = s.split("</head>", 1)[1]
    body = re.sub(r"^\s*<body[^>]*>", "", body)
    body = re.sub(r"</body>\s*</html>\s*$", "", body.strip())
    body = re.sub(r'<div class="rtag">.*?</div></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<header class="hd">.*?</header>\s*', "@@TOP@@\n", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="way".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="w"><p class="crumb">.*?</p></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<footer class="ft">.*?</footer>\s*', "@@END@@\n", body, count=1, flags=re.S)
    body = re.sub(r'<section class="pages".*?</section>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="bn".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<script src="1119_授業の色づけ\.js"></script>\s*', "", body)
    body = re.sub(r"\n?<!--.*?-->", "", body, flags=re.S)
    r = P.rel_root(path)
    body = fix_urls(body, r)
    for k, fn in ROUGH_FILES.items():
        body = body.replace(f'href="{fn}', f'href="{ROUGH_URL[k]}')
    body = body.replace('/exam/#', "/exam/#")
    body = body.replace('href="https://carepicnic.com/', 'href="/')
    return body


# 勉強の道の行き先（ラフ01 の STEP1〜5 の言葉 → 本番の住所）。どのページの「次の一歩」もここから引く
MICHI_ITEMS = {
    "学科の勉強法": "/exam-guide/gakka-benkyoho/",
    "試験の難易度と合格率": "/exam-guide/goukakuritsu/",
    "ことば図鑑": "/terms/", "理論家図鑑": "/theorists/",
    "法改正・時事の掲示板": "/laws/",
    "労働法のまちがえやすい4つ": "/exam-guide/rodo-hikkake/",
    "白書・調査・報告書の要点": "/exam-guide/shiryo/",
    "1問1答ドリル": "/games/quiz/",
    "学科の模擬試験 全10回": "/exam-guide/moshi/",
    "論述の模擬試験 全16回": "/exam-guide/ronjutsu-moshi/",
    "論述の型ノート（無料PDF）": "/exam-guide/ronjutsu-kata/",
    "試験まで30日の逆算プラン": "/exam-guide/last-30days/",
    "直前対策テキスト（PDF）": "/text/",
    "お守りページ": "/omamori/",
}


def link_items(body):
    """「次の一歩」のカード（ncard）の行き先を、カードの言葉から本番の住所にする"""
    def fix(m):
        a = m.group(0)
        t = re.search(r'<span class="tl">(.*?)</span>', a)
        if t and t.group(1) in MICHI_ITEMS:
            a = re.sub(r'href="[^"]*"', f'href="{MICHI_ITEMS[t.group(1)]}"', a, count=1)
        return a
    return re.sub(r'<a class="ncard"[^>]*>.*?</a>', fix, body, flags=re.S)


def split_scripts(body):
    """本文の最後の <script> のまとまりを分ける → (本文, [script…])"""
    scripts = []
    while True:
        m = re.search(r"\s*(<script\b[^>]*>(?:(?!</script>).)*</script>)\s*$", body, re.S)
        if not m:
            break
        scripts.insert(0, m.group(1))
        body = body[:m.start()]
    return body, scripts


# ---------------------------------------------------------------- 頭
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500&family=Zen+Kaku+Gothic+New:wght@500;700&family=Zen+Kurenaido&display=swap" rel="stylesheet">')


def prod_head_parts(prod_html):
    """本番のページの頭から、計測（最初の <script>）・meta・canonical・OGP・アイコン・構造化データ"""
    h = prod_html.split("</head>", 1)[0]
    analytics = re.search(r"(<!--[^>]*アクセス解析.*?-->\s*)?<script>\s*window\.dataLayer.*?</script>", h, re.S)
    keep = []
    for pat in (r'<meta name="viewport"[^>]*>', r"<title>.*?</title>", r'<meta name="description"[^>]*>',
                r'<meta name="robots"[^>]*>', r'<link rel="canonical"[^>]*>', r'<meta property="og:[^"]+"[^>]*>',
                r'<meta name="twitter:[^"]+"[^>]*>', r'<link rel="icon"[^>]*>', r'<link rel="apple-touch-icon"[^>]*>'):
        keep += re.findall(pat, h, re.S)
    ld = re.findall(r'<script type="application/ld\+json">.*?</script>', h, re.S)
    return (analytics.group(0) if analytics else ""), "\n".join(keep), ld


def css_links(path, cat, extra=()):
    r = P.rel_root(path)
    # ラフと同じ順：kata.css → 型の見た目 → 12枚で共通の tooitsu-1119 など
    out = [f'<link rel="stylesheet" href="{r}css/kata.css?v={CSS_VER}">',
           f'<link rel="stylesheet" href="{r}css/shiken/{cat}.css?v={CSS_VER}">',
           f'<link rel="stylesheet" href="{r}css/kata-shiken.css?v={CSS_VER}">']
    for e in extra:
        out.append(f'<link rel="stylesheet" href="{r}css/{e}?v={CSS_VER}">')
    out.append(f'<link rel="stylesheet" href="{r}css/kata-shiken-plus.css?v={CSS_VER}">')
    return "\n".join(out)


def page(path, prod_html, body, cat, crumb, extra_css=(), head_extra="", ld_fix=None):
    """1ページを組み立てて書く。body は rough_body() を直したもの（@@TOP@@・@@END@@ 入り）。
    @@MAIN@@ と @@/MAIN@@ の間を <main id="main"> にする（なければ @@TOP@@ のあと〜@@END@@ の前）"""
    analytics, meta, ld = prod_head_parts(prod_html)
    if ld_fix:
        ld = ld_fix(ld)
    head = "\n".join(x for x in [
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">', analytics, meta, FONTS,
        css_links(path, cat, extra_css), *ld, head_extra, P.css_link(path), "</head>",
    ] if x)
    top = P.top_parts(path, "")
    crumb_html = P.crumb_html(crumb)
    if "@@MAIN@@" not in body:
        body = body.replace("@@TOP@@\n", "@@TOP@@\n@@MAIN@@\n", 1).replace("@@END@@", "@@/MAIN@@\n@@END@@", 1)
    body = body.replace("@@TOP@@\n", top, 1)
    body = body.replace("@@MAIN@@\n", f'<main id="main" class="kmain">\n{crumb_html}\n', 1)
    body = body.replace("@@/MAIN@@\n", "</main>\n", 1)
    body = body.replace("@@END@@\n", P.end_parts(path), 1)
    out = head + '\n<body class="kata">\n<a class="skip-link" href="#main">本文へ移動</a>\n' + body.strip() + "\n</body>\n</html>\n"
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(out)
    return out


def check(path, out):
    """気になる文字（ラフの名残・手元の住所・空のリンク）を数える"""
    bad = {}
    for x in ("file://", "1115_Canvaの絵入り_素材", "1119_ラフ", "ラフ：", "Projects/", 'href="#"', "common.css",
              "1119_授業の色づけ", "xLessonSync", "仮）", "（仮"):
        n = out.count(x)
        if n:
            bad[x] = n
    imgs = re.findall(r'(?:src|href)="([^"#?]+\.(?:webp|png|jpg|svg|pdf|css|js))', out)
    imgs += re.findall(r'url\("?([^")]+\.(?:webp|png|jpg))', out)
    base = os.path.dirname(os.path.join(ROOT, path))
    missing = sorted({i for i in imgs if not i.startswith(("http", "data:", "/")) and not os.path.exists(os.path.normpath(os.path.join(base, i)))})
    missing += sorted({i for i in imgs if i.startswith("/") and not i.startswith("//") and not os.path.exists(os.path.join(ROOT, i.lstrip("/")))})
    print(f"{path}: {len(out)//1024}KB  気になる文字: {bad or 'なし'}  ない絵・ファイル: {missing or 'なし'}")
    return bad, missing


if __name__ == "__main__":
    prepare()
    print("prepared")
