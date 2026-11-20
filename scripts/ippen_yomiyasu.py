#!/usr/bin/env python3
"""学校えらびの側の「読みやすさ」の仕上げ（2026-11-20 ナデシコ）。

ちゃん「ボタンの位置やテキストがぎゅうぎゅうなところを確認してください。
あと見出しの改行も調整して読者が読みやすくしてください」

やること（言葉は変えない）
- <body> に data-yomi をつける。css/kyoutsu.css の [data-yomi] の決まり（ボタンのまわり・箱の中の余白）は、
  この印があるページだけに効く（試験の側のページには効かない）
- 見出し（h1・h2・h3）と、カードの題（比較表の学校名・40の疑問の問い・次の一歩のカード）を文節で折る：
  中に <wbr> がなければ BudouX で文節の切れ目に <wbr> を入れ、class に bk を足す。
  .bk は word-break:keep-all（<wbr> と句読点でだけ折れる）＋ text-wrap:balance（行の長さをそろえる）
- 何度かけても同じ結果になる（bk がついた所はさわらない）。<script>・<style>・<template> の中はさわらない

生成の道具（ippen_from_rough.build・ippen_build_guides・ippen_build_gimon）は、書き出す直前にこれを通す。
手で組んだページ（トップ・比較表）は、直したあとに次で通す：
使い方: python3 scripts/ippen_yomiyasu.py [ページ …]（なければ下の PAGES）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    "index.html",
    "schools/index.html", "schools/compare/index.html",
    "schools/lec/index.html", "schools/chiiki-renkei-platform/index.html",
    "schools/nippon-manpower/index.html", "schools/recurrent/index.html",
    "school-guides/dokugaku/index.html", "school-guides/how-to-choose/index.html",
    "school-guides/kyufukin/index.html", "school-guides/kyufukin-tetsuzuki/index.html",
    "school-guides/merit-demerit/index.html", "school-guides/online/index.html",
    "school-guides/training-and-exam-preparation/index.html", "school-guides/working-mothers/index.html",
    "school-guides/yasui/index.html", "school-guides/zaitaku-fukugyo/index.html",
    "school-guides/zaitaku-kokka-shikaku/index.html",
    "shikaku-guide/gimon/index.html",
]

try:
    import budoux
    _PARSER = budoux.load_default_japanese_parser()
except ImportError:  # 道具がないときは、<wbr> のない見出しには bk をつけない（keep-all だけでは折れなくなるため）
    _PARSER = None

# 見出しとカードの題（中に同じ名前のタグを入れ子にしないもの）
TARGETS = [
    re.compile(r'<(h1|h2|h3)\b([^>]*)>(.*?)</\1>', re.S),
    re.compile(r'<(span)\b([^>]*\bclass="(?:cmp__name|nn|gimon__q|gimon__a)"[^>]*)>((?:(?!<span\b).)*?)</span>', re.S),
    # 広告の札の1行（「紹介リン｜ク」と折れないように）
    re.compile(r'<(summary)\b([^>]*\bclass="disclosure__title"[^>]*)>(.*?)</summary>', re.S),
]
MASK = re.compile(r'<(script|style|template)\b.*?</\1>', re.S | re.I)
TOKEN = re.compile(r'(<[^>]+>|&#?\w+;)')


# BudouX が1つにまとめる長い名前は、意味の切れ目でも折れるようにする（狭いカード・表の頭で「プラットフォ｜ーム」とならないように）
WORDS = {
    "地域連携プラットフォーム": "地域連携<wbr>プラットフォーム",
    "LEC東京リーガルマインド": "LEC<wbr>東京リーガルマインド",
    "日本産業カウンセラー協会": "日本産業<wbr>カウンセラー協会",
    "キャリアコンサルタント養成講座": "キャリアコンサルタント<wbr>養成講座",
}


def phrase(inner):
    """タグと文字参照はそのまま、文字の所だけ文節の切れ目に <wbr> を入れる"""
    out = []
    for part in TOKEN.split(inner):
        if not part or TOKEN.fullmatch(part) or not part.strip():
            out.append(part)
            continue
        s = "<wbr>".join(_PARSER.parse(part))
        for a, b in WORDS.items():
            s = s.replace(a, b)
        out.append(s)
    return "".join(out)


def add_class(attrs, name="bk"):
    m = re.search(r'\bclass="([^"]*)"', attrs)
    if m:
        if name in m.group(1).split():
            return attrs
        return attrs[:m.start()] + f'class="{m.group(1)} {name}"' + attrs[m.end():]
    return f' class="{name}"' + attrs if not attrs.startswith(" ") else f' class="{name}"{attrs}'


def _one(m):
    tag, attrs, inner = m.group(1), m.group(2), m.group(3)
    cls = re.search(r'\bclass="([^"]*)"', attrs)
    if cls and "bk" in cls.group(1).split():
        return m.group(0)
    text = re.sub(r"<[^>]+>", "", inner)
    if not re.search(r"[぀-ヿ一-鿿]", text):
        return m.group(0)
    if "<wbr" not in inner:
        if _PARSER is None:
            return m.group(0)
        inner = phrase(inner)
    return f"<{tag}{add_class(attrs)}>{inner}</{tag}>"


def apply(html):
    masks = []

    def keep(m):
        masks.append(m.group(0))
        return f"\x00{len(masks) - 1}\x00"

    s = MASK.sub(keep, html)
    for rx in TARGETS:
        s = rx.sub(_one, s)
    s = re.sub(r"<body\b(?![^>]*\bdata-yomi\b)([^>]*)>", r"<body\1 data-yomi>", s, count=1)
    return re.sub(r"\x00(\d+)\x00", lambda m: masks[int(m.group(1))], s)


def main():
    files = sys.argv[1:] or PAGES
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(ROOT, f)
        if not os.path.exists(p):
            print(f"  なし: {f}")
            continue
        s = open(p, encoding="utf-8").read()
        new = apply(s)
        n = new.count(' bk"') + new.count('"bk"') - s.count(' bk"') - s.count('"bk"')
        if new != s:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
        print(f"{f}: 見出し・題 {n} か所に印{'（変わりなし）' if new == s else ''}")


if __name__ == "__main__":
    main()
