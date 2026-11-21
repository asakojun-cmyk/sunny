#!/usr/bin/env python3
"""11/21 試験対策のページ（/exam/）を、ちゃんがOKしたラフ 案B1 で入れかえる道具。何回動かしても同じ結果。

元のラフ：picnic-docs/1108_サイトの設計/イメージ/ラフ_1119_試験の側/1121_ラフ_12_試験対策_案B1.html
決めごと：同じフォルダの 1121_指示書_試験対策ページのリニューアル.md（「11/21 ちゃんが決めたこと」）

ほかのページ（scripts/ippen_from_rough.py）と同じ決まりで組む
- 頭：計測・canonical・OGP・アイコンは本番の exam/index.html から引きつぐ。title と説明文はラフの中身に合わせる
  （1回組んだあとは本番の頭＝この道具が書いた頭なので、何回かけても同じ）
- ヘッダー・道しるべ・パンくず・フッター・下のメニューは scripts/ippen_parts.py の共通の部品
- ラフの <style>（シンさんの直し blue1121・step3fix・picnicfix、ナデシコの直しを含む）と <script>（blue1121js を含む）は
  中身をそのまま持ってくる。CSS の中の作業メモ（/* … */）だけ外す（見た目は変わらない）
- ラフの印（rtag）・作業メモのコメント・file:// や ../../ の住所は残さない
- 絵：ラフの ../../…/Projects/<リポジトリ>/img/… は本番の img/… へ。本番に無ければ元のリポジトリから写す。
  ラフの素材フォルダ（1115_Canvaの絵入り_素材 など）の png は webp にして img/kata/ か img/exam/ に置く
- リンク：https://carepicnic.com/〜 は /〜/ にそろえる。ラフどうしのリンク（〜.html）で本番に無いものは、
  文字だけ（押せない）にして、最後に「無いページ」として出す（勝手に消さない）
- 試験の側のページなので ippen_yomiyasu（data-yomi＝学校えらびの側の決まり）は通さない。
  スマホの見やすさ（scripts/ippen_sp_1121.py の body.kata 用）は、全ページと同じく入れる

使い方：python3 scripts/ippen_exam_1121.py
"""
import hashlib
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ippen_parts as P  # noqa: E402
import ippen_from_rough as F  # noqa: E402
import ippen_sp_1121 as SP  # noqa: E402

ROOT = P.ROOT
PATH = "exam/index.html"
ROUGH_DIR = "/Users/iwawakiasako/Documents/Obsidian Vault/GitHub/picnic-docs/1108_サイトの設計/イメージ/ラフ_1119_試験の側"
ROUGH = os.path.join(ROUGH_DIR, "1121_ラフ_12_試験対策_案B1.html")
PROJECTS = "/Users/iwawakiasako/Projects"
CRUMB = [("ホーム", "/"), ("試験対策", None)]

# ラフの素材フォルダの絵 → 本番での名前（日本語の名前はローマ字にする）
NAMES = {
    "hero_移動図書館_空を透明に.png": "img/kata/hero_idou_toshokan.webp",
}

log_copy, log_missing_img, log_nolink = [], [], []


def to_webp(src, dst):
    from PIL import Image
    im = Image.open(src)
    if im.width > 2000:
        im = im.resize((2000, round(im.height * 2000 / im.width)), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, "WEBP", quality=84, method=6)


def site_img_from_repo(m):
    """../../…/Projects/<repo>/img/X → img/X（本番に無ければ写す）"""
    repo, sub = m.group(1), m.group(2)
    dst = os.path.join(ROOT, "img", sub)
    if not os.path.exists(dst):
        src = os.path.join(PROJECTS, repo, "img", sub)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            log_copy.append(f"{src} → img/{sub}")
        else:
            log_missing_img.append(f"img/{sub}（{repo} にも無い）")
    return "../img/" + sub


def site_img_from_sozai(rel):
    """ラフのフォルダからの相対の住所（素材フォルダの png など）→ 本番の webp"""
    src = os.path.normpath(os.path.join(ROUGH_DIR, rel))
    name = os.path.basename(src)
    sub = NAMES.get(name)
    if not sub:
        base = os.path.splitext(name)[0]
        if re.fullmatch(r"[A-Za-z0-9_.-]+", base):
            sub = f"img/exam/{base}.webp"
        else:
            sub = f"img/exam/e_{hashlib.sha1(name.encode()).hexdigest()[:8]}.webp"
            print(f"  ※ 名前をローマ字にできなかった絵：{name} → {sub}（NAMES に足すと名前を決められる）")
    dst = os.path.join(ROOT, sub)
    if not os.path.exists(dst):
        if not os.path.exists(src):
            log_missing_img.append(f"{rel}（元の素材が無い）")
            return "../" + sub
        if src.lower().endswith(".webp"):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        else:
            to_webp(src, dst)
        log_copy.append(f"{src} → {sub}")
    return "../" + sub


def fix_paths(s):
    # 1) リポジトリの img
    s = re.sub(r'(?:\.\./)+Projects/(sunny-rough1117-dan1|sunny-ippen|sunny)/img/([^"\')\s]+)', site_img_from_repo, s)
    # 2) ラフの素材フォルダ（../1115_… など、ラフのフォルダからの相対で、絵のもの）
    s = re.sub(r'(?<=["\'(])((?:\.\./)+[^"\')\s]+?\.(?:png|jpe?g|webp))(?=["\')])',
               lambda m: m.group(1) if m.group(1).startswith("../img/") else site_img_from_sozai(m.group(1)), s)
    return s


def fix_links(body):
    body = body.replace("https://carepicnic.com/", "/")
    # ラフどうしのリンク（〜.html）：本番に無いので文字だけにする
    def nolink(m):
        log_nolink.append(f"{m.group(1)}（「{re.sub(r'<[^>]+>', '', m.group(2))}」）")
        return f'<span class="x-nolink">{m.group(2)}</span>'
    body = re.sub(r'<a href="((?!/|#|https?:)[^"]+\.html)">(.*?)</a>', nolink, body)
    return body


def strip_css_comments(style):
    return re.sub(r"/\*.*?\*/", "", style, flags=re.S)


def build():
    src = open(ROUGH, encoding="utf-8").read()
    src = fix_paths(src)
    rhead, rbody = src.split("</head>", 1)
    title = re.search(r"<title>(.*?)</title>", rhead, re.S).group(1).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', rhead).group(1)
    # 頭：本番から引きつぎ、title と説明文だけラフに合わせる
    meta = F.head_from_prod(open(os.path.join(ROOT, PATH), encoding="utf-8").read())
    meta = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", meta, flags=re.S)
    meta = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', meta)
    meta = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', meta)
    meta = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', meta)
    url = "https://carepicnic.com/exam/"
    ld = ('<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
          '{"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://carepicnic.com/"}, '
          f'{{"@type": "ListItem", "position": 2, "name": "試験対策", "item": "{url}"}}]}}</script>\n'
          '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebPage", '
          f'"name": "{title.split("｜キャリコン学びピクニック")[0]}", "description": "{desc}", "url": "{url}", "inLanguage": "ja", '
          '"dateModified": "2026-11-21", "isPartOf": {"@type": "WebSite", "name": "キャリコン学びピクニック", "url": "https://carepicnic.com"}}</script>')
    styles = [strip_css_comments(x) for x in re.findall(r"<style\b.*?</style>", rhead, re.S)]
    nolink_css = '<style id="exam1121">body.kata .x-nolink{font-size:15.5px;color:var(--ink)}</style>'
    head = "\n".join([
        '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">', F.ANALYTICS, meta, F.FONTS,
        f'<link rel="stylesheet" href="../css/kata.css?v={P.CSS_VER}">', ld, *styles, nolink_css, P.css_link(PATH),
        SP.block(SP.KATA).rstrip("\n"), "</head>",
    ])
    # 本文：ラフの印・ラフの部品を外す（ippen_from_rough と同じ）
    body = rbody
    body = re.sub(r'<div class="rtag">.*?</div></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<header class="hd">.*?</header>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="way".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="w"><p class="crumb">.*?</p></div>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<footer class="ft">.*?</footer>\s*', "@@END@@\n", body, count=1, flags=re.S)
    body = re.sub(r'<nav class="bn".*?</nav>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r"\n?<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"(<style\b.*?</style>)", lambda m: strip_css_comments(m.group(1)), body, flags=re.S)
    body = fix_links(body)
    # 計測の印（見た目は同じ）：悩みのボタン
    body = re.sub(r'<button class="c" type="button" data-k="(\w+)"', r'<button class="c" type="button" data-k="\1" data-ev="exam_q_\1"', body)
    top = P.top_parts(PATH, P.crumb_html(CRUMB))
    body = re.sub(r"(<body[^>]*>\s*<svg.*?</svg>\s*)", lambda m: m.group(1) + top + "\n", body, count=1, flags=re.S)
    body = body.replace("@@END@@\n", P.end_parts(PATH))
    out = head + body
    with open(os.path.join(ROOT, PATH), "w", encoding="utf-8") as fh:
        fh.write(out)
    return out


def check_links(out):
    bad = []
    hrefs = set(re.findall(r'href="(/[^"]*)"', out)) | set(re.findall(r'\bu:"(/[^"]*)"', out))
    for h in sorted(hrefs):
        p, _, frag = h.partition("#")
        f = os.path.join(ROOT, p.lstrip("/"))
        if p.endswith("/") or p == "":
            f = os.path.join(f, "index.html")
        if not os.path.exists(f):
            bad.append(h + "（ページが無い）")
            continue
        if frag:
            t = open(f, encoding="utf-8").read()
            if not re.search(r'\bid="%s"' % re.escape(frag), t):
                bad.append(h + "（ページはあるが、#" + frag + " の場所が無い）")
    for h in sorted(set(re.findall(r'href="#([^"]+)"', out))):
        if h != "sitemap" and not re.search(r'\bid="%s"' % re.escape(h), out):
            bad.append("#" + h + "（このページに場所が無い）")
    return hrefs, bad


if __name__ == "__main__":
    out = build()
    hrefs, bad = check_links(out)
    leftover = [x for x in ("file://", "Projects/", "1115_Canva", "ラフ", "rtag", 'href="#"', "../../", "carepicnic.com/exam-guide")
                if x in out.split("</head>", 1)[1]]
    print(f"{PATH}: {len(out)//1024}KB")
    print("写した絵：", *(log_copy or ["なし（全部本番の img/ にあった）"]), sep="\n  ")
    print("見つからない絵：", *(log_missing_img or ["なし"]), sep="\n  ")
    print(f"サイトの中のリンク {len(hrefs)} 本  無い・場所が無い：", *(bad or ["なし"]), sep="\n  ")
    print("ラフどうしのリンク（本番に無い・文字だけにした）：", *(log_nolink or ["なし"]), sep="\n  ")
    print("残っていた気になる文字：", leftover or "なし")
