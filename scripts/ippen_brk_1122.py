#!/usr/bin/env python3
"""スマホで語の途中で改行しないようにする仕上げ（2026-11-22 イワカガミ）。

ちゃん 11/22「新しくリニューアルしたページをすべて確認して、スマホで崩れていないか、
変な場所で改行されていないかなど確認をお願いします」
→ 375・390幅で「地域連携プラットフォ／ーム」「ハロ／ーワーク」のような語の途中の改行が約120か所。

やること（言葉は変えない）
- 本文の文字に、BudouX で文節の切れ目に <wbr> を入れる。
  ひとかたまりの文（ブロックの要素から次のブロックの要素まで。a・span・strong・small などの中も続けて1つ）
  の中に <wbr> がすでにあれば、そのかたまりはさわらない（exam/ の brk1121、ippen_yomiyasu の見出しなど）。
- script・style・pre・code・template・textarea・svg・ruby・option・title の中、タグの属性（JSON-LD もふくむ）はさわらない。
- <style id="brk1122"> を1つ足す：<wbr> をふくむ本文の要素だけ word-break:keep-all（<wbr> と句読点でだけ折れる）
  ＋ overflow-wrap:anywhere（長い英数字やURLははみ出さずに折れる）。
  :has(wbr) にしたのは、JS があとから入れる文字（<wbr> がない）を keep-all にして折れなくしないため。
- 何度かけても同じ結果になる（<wbr> がある所はさわらない・style は id で1つだけ）。

ページを作り直す台本（ippen_build_*・ippen_exam_1121.py・ippen_top_match_1121.py など）を流したあとに通す：
使い方: python3 scripts/ippen_brk_1122.py [ページ …]（なければ下の PAGES）
"""
import os
import re
import sys

import budoux

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from ippen_yomiyasu import WORDS as _YWORDS
except Exception:  # noqa: BLE001
    _YWORDS = {}

PAGES = [
    "index.html",
    "exam/index.html", "careers/index.html", "exam-guide/mensetsu-renshuukai/index.html",
    "school-guides/dokugaku/index.html", "school-guides/how-to-choose/index.html",
    "school-guides/kyufukin-tetsuzuki/index.html", "school-guides/kyufukin/index.html",
    "school-guides/merit-demerit/index.html", "school-guides/online/index.html",
    "school-guides/training-and-exam-preparation/index.html", "school-guides/working-mothers/index.html",
    "school-guides/yasui/index.html", "school-guides/zaitaku-fukugyo/index.html",
    "school-guides/zaitaku-kokka-shikaku/index.html",
    "school-reviews/chiiki-renkei-platform/index.html",
    "schools/index.html", "schools/chiiki-renkei-platform/index.html", "schools/compare/index.html",
    "schools/lec/index.html", "schools/nippon-manpower/index.html", "schools/recurrent/index.html",
    "shikaku-guide/gimon/index.html", "shikaku-guide/index.html",
]

PARSER = budoux.load_default_japanese_parser()

# 長い名前は意味の切れ目でも折れるように（狭い表の頭・カードで、はみ出さず・語の途中で切れず）
WORDS = dict(_YWORDS)

# 中をさわらない要素
SKIP = {"script", "style", "pre", "code", "template", "textarea", "svg", "ruby", "option", "select",
        "title", "head", "noscript", "math", "kbd", "samp", "var"}
# 文の中に入る要素（ここではかたまりを切らない）
INLINE = {"a", "span", "strong", "b", "em", "i", "small", "br", "wbr", "mark", "sup", "sub", "u", "s",
          "abbr", "time", "img", "q", "cite", "dfn", "data", "bdi", "bdo", "del", "ins", "label", "picture",
          "source"}
VOID = {"br", "wbr", "img", "source", "input", "meta", "link", "hr", "area", "base", "col", "embed",
        "param", "track"}

TOKEN = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<![^>]*>|<[^>]+>", re.S)
ENT = re.compile(r"(&#?\w+;)")
TAGNAME = re.compile(r"</?\s*([a-zA-Z][\w:-]*)")
JA = re.compile(r"[぀-ヿ一-鿿]")

CSS = (
    '<style id="brk1122">'
    "/* 11/22 スマホの改行：<wbr>（scripts/ippen_brk_1122.py が文節に入れた）と句読点でだけ折る。長い英数字は枠の中で折る */"
    ":is(h1,h2,h3,h4,p,li,a,dt,dd,th,td,span,small,figcaption,summary,button,strong,b,label):has(wbr)"
    "{word-break:keep-all;overflow-wrap:anywhere}"
    # 11/22 ちゃん「Aが美しい」：スマホの両端そろえの本文（.sp-j）は、中の太字やリンクもふくめて今までどおりの折り方に
    "@media (max-width:700px){.sp-j :is(a,span,small,strong,b,label){word-break:normal!important;overflow-wrap:normal!important}}"
    # 11/22 カタカナ語は途中で折らない（表・見出し・カード）。本文（.sp-j）は今までどおり
    # 印の span には、ページの「◯◯ span {…}」の見た目が当たらないように打ち消す（文字の見た目は親のまま）
    # （:not(#brk) は強さを上げるため。「body.kata .ft-row span{…!important}」などにも勝つ）
    ":is(.kn,.knw):not(#brk){all:unset!important}"
    "span.kn:not(#brk){white-space:nowrap!important}.sp-j span.kn:not(#brk){white-space:normal!important}"
    "</style>"
)

# カタカナ語（3字以上・「・」でつながる名前もふくむ）
KANA_RUN = re.compile(r"[ァ-ヺ][ァ-ヺー]{2,}(?:・[ァ-ヺ][ァ-ヺー]+)*")
# 長いカタカナ語を折ってよい部品
KANA_PARTS = ["キャリア", "コンサルタント", "コンサルティング", "プラットフォーム", "カウンセリング", "カウンセラー",
              "マネージメント", "マネジメント", "カレッジ", "オンライン", "スクーリング", "ハローワーク", "センター",
              "サービス", "インターネット", "ホームワーク", "マインド", "システム", "プログラム", "コース", "クラス"]
KN_OPEN = '<span class="kn">'


def kana_chunks(word):
    """長い語を「・」と部品の切れ目で分ける（短い語はそのまま1つ）"""
    out = []
    for seg in re.findall(r"[^・]+・?", word):
        if len(seg) <= 8:
            out.append(seg)
            continue
        rest = seg
        while rest:
            p = next((p for p in KANA_PARTS if rest.startswith(p)), None)
            if p:
                out.append(p)
                rest = rest[len(p):]
                continue
            nxt = next((i for i in range(1, len(rest)) if any(rest[i:].startswith(q) for q in KANA_PARTS)), len(rest))
            out.append(rest[:nxt])
            rest = rest[nxt:]
    # 「ー」や「・」だけの切れはしは前にくっつける
    merged = []
    for c in out:
        if merged and (len(c.rstrip("・")) <= 1):
            merged[-1] += c
        else:
            merged.append(c)
    return merged


def kana_wrap(html_text):
    """文字の所だけ、カタカナ語を <span class="kn"> で包む（タグ・文字参照はさわらない）"""
    out = []
    for part in re.split(r"(<[^>]+>|&#?\w+;)", html_text):
        if not part or part.startswith("<") or part.startswith("&"):
            out.append(part)
            continue
        out.append(KANA_RUN.sub(lambda m: "<wbr>".join(KN_OPEN + c + "</span>" for c in kana_chunks(m.group(0))), part))
    return "".join(out)


def phrase(text):
    """文字参照はそのまま、文字の所だけ文節の切れ目に <wbr> を入れる"""
    out = []
    for part in ENT.split(text):
        if not part or ENT.fullmatch(part) or not JA.search(part):
            out.append(part)
            continue
        # 前後の空白・改行はそのまま残す
        m = re.match(r"(\s*)(.*?)(\s*)$", part, re.S)
        lead, core, tail = m.groups()
        s = "<wbr>".join(PARSER.parse(core))
        # カタカナの語の中では折らない（「プラットフォ／ーム」にしない）
        s = re.sub(r"(?<=[ァ-ヺー])<wbr>(?=[ァ-ヺー])", "", s)
        # 記号の前で折れる形にしない（行頭に ）」、。 が来ないように）
        s = re.sub(r"<wbr>(?=[、。，．）」』】〕！？!?・〜…：:%％])", "", s)
        # 長い名前は、決めた切れ目だけで折る
        for a, b in WORDS.items():
            if a in core:
                rx = "(?:<wbr>)?".join(re.escape(ch) for ch in a)
                s = re.sub(rx, b, s)
        out.append(lead + s + tail)
    return "".join(out)


def apply(html):
    if "<body" not in html:
        return html
    head_end = html.index("<body")
    head, body = html[:head_end], html[head_end:]

    pieces = []          # 出力
    run = []             # いまのかたまり（('t', 文字) / ('g', タグ)）
    skip_stack = []      # SKIP の中にいるか

    def flush():
        if not run:
            return
        has_wbr = any(k == "g" and re.match(r"<wbr\b", v, re.I) for k, v in run)
        prev = None
        depth = 0  # かたまりの中の a・span などの深さ
        items = []  # (html, いちばん外の文字か <wbr> か, カタカナを包んだか)
        for k, v in run:
            if k == "t":
                # すでに <span class="kn"> の中なら包まない（何度かけても同じに）
                inside_kn = prev == KN_OPEN
                t = v if has_wbr else phrase(v)
                w = t if inside_kn else kana_wrap(t)
                # span なども横並びの箱になっていることがあるので、深さは問わない（続く文字と <wbr> は同じ親の中）
                items.append((w, True, w != t))
            else:
                is_wbr = bool(re.match(r"<wbr\b", v, re.I))
                items.append((v, is_wbr, False))
                tm2 = TAGNAME.match(v)
                if tm2 and tm2.group(1).lower() not in VOID and not v.endswith("/>"):
                    depth += -1 if v.startswith("</") else 1
                    depth = max(depth, 0)
            prev = v if k == "g" else None
        # 横並び（flex・grid）の箱の中で文が分かれないよう、いちばん外で続く文字と <wbr> をまとめて1つに包む
        i = 0
        while i < len(items):
            if not items[i][1]:
                pieces.append(items[i][0])
                i += 1
                continue
            j = i
            while j < len(items) and items[j][1]:
                j += 1
            seg = items[i:j]
            html_seg = "".join(x[0] for x in seg)
            if any(x[2] for x in seg):
                m = re.match(r"(\s*)(.*?)(\s*)$", html_seg, re.S)
                html_seg = m.group(1) + '<span class="knw">' + m.group(2) + "</span>" + m.group(3)
            pieces.append(html_seg)
            i = j
        run.clear()

    pos = 0
    for m in TOKEN.finditer(body):
        if m.start() > pos:
            txt = body[pos:m.start()]
            if skip_stack:
                pieces.append(txt)
            else:
                run.append(("t", txt))
        tag = m.group(0)
        pos = m.end()
        tm = TAGNAME.match(tag)
        if not tm:  # コメントなど
            if skip_stack:
                pieces.append(tag)
            else:
                run.append(("g", tag))
            continue
        name = tm.group(1).lower()
        closing = tag.startswith("</")
        if skip_stack:
            pieces.append(tag)
            if name == skip_stack[-1]:
                if closing:
                    skip_stack.pop()
                elif not tag.endswith("/>"):
                    skip_stack.append(name)
            continue
        if name in SKIP:
            flush()
            pieces.append(tag)
            if not closing and not tag.endswith("/>"):
                skip_stack.append(name)
            continue
        if name in INLINE:
            run.append(("g", tag))
            continue
        # ブロックの境目
        flush()
        pieces.append(tag)
    if pos < len(body):
        if skip_stack:
            pieces.append(body[pos:])
        else:
            run.append(("t", body[pos:]))
    flush()
    body = "".join(pieces)

    if 'id="brk1122"' in head:
        head = re.sub(r'<style id="brk1122">.*?</style>', lambda m: CSS, head, count=1, flags=re.S)
    else:
        head = head.replace("</head>", CSS + "\n</head>", 1) if "</head>" in head else head + CSS
    return head + body


def main():
    files = sys.argv[1:] or PAGES
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(ROOT, f)
        if not os.path.exists(p):
            print(f"  なし: {f}")
            continue
        s = open(p, encoding="utf-8").read()
        new = apply(s)
        n = new.count("<wbr>") - s.count("<wbr>")
        if new != s:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new)
        print(f"{f}: <wbr> +{n}{'（変わりなし）' if new == s else ''}")


if __name__ == "__main__":
    main()
