#!/usr/bin/env python3
"""11/21 スマホの見やすさの直し。何回かけても同じ（<style id="sp1121"> を入れかえる）。

ちゃん「キャリコン学びピクニックの全ページ。スマホに対応させて。トップは対応していない。みにくい。
あと人物のイラスト画像が点滅してる。文字が読みにくい」

- 点滅：人物の絵の白いふちを SVG のフィルター（filter:url(#sticker)）で付けていた。iPhone の Safari では、
  拡大・かしげる動き・スクロールのたびに描き直されてチカチカしやすい。スマホ（指で触る画面・幅700px以下）では、
  ふつうの CSS の影を重ねた白いふちにかえる（見た目はほぼ同じ）。
- 文字：トップと学校・ガイドのページ（body.kata）は、スマホで字と字のあいだが 0.08〜0.10em と広く、
  本文が 13〜14.5px と小さかった。字のあいだを 0.03em に、本文を 15〜16px に上げる。
  試験の側の古い型のページ（17px・0.03em）は、もう読みやすいのでさわらない。
- 組み（段の順番・絵の場所）は変えない。
使い方：python3 scripts/ippen_sp_1121.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FUCHI = ("drop-shadow(2.5px 0 0 #fff) drop-shadow(-2.5px 0 0 #fff) drop-shadow(0 2.5px 0 #fff) "
         "drop-shadow(0 -2.5px 0 #fff) drop-shadow(0 2px 3px rgba(46,74,120,.18))")
SP = "@media (max-width:700px),(hover:none)"
PH = "@media (max-width:700px)"

TOP = f"""
{SP}{{
  .person .pic,.hitokoto .hpic{{filter:{FUCHI}!important;will-change:auto}}
  .person .pic img,.hitokoto .hpic img{{filter:none!important}}
}}
{PH}{{
  body p,body li,body td,body th,body dd,body summary,body small,body figcaption,body .fuki,body a{{letter-spacing:.03em!important}}
  body h1,body h2,body h3{{letter-spacing:.05em!important}}
  body div.a>p,body .lead p.plain,body div.body>p,body tr>td,body th>a,body details>summary,body li>span.a,body p.ptxt,body p.lead-h{{font-size:16px!important;line-height:1.85!important}}
  body article.card>p.forwho,body .body>p.kyufu-note,body li.wari>p.cond,body .hb p.ht{{font-size:15px!important}}
  body td>small,body td.ex>small,body p.exam-lead>small,body .fee p.tot1,body .fee p.lb2,body .col p.ref.note,body p.note,body .kf-wrap p.zentei{{font-size:14px!important}}
  body p.src,body p.src a,body .days p.dnote,body .notes>p,body .fuki2 small,body li.wari>small{{font-size:13.5px!important}}
  body li>a{{font-size:14px}}
  body .person .fuki{{font-size:14.5px!important;line-height:1.6}}
}}
"""

KATA = f"""
{SP}{{
  body.kata .mpic{{filter:{FUCHI}!important}}
  body.kata .who1 .hito{{filter:none!important}}
}}
{PH}{{
  body.kata p,body.kata li,body.kata dd,body.kata td,body.kata th,body.kata figcaption,body.kata small,body.kata summary,body.kata a{{letter-spacing:.03em!important}}
  body.kata h1,body.kata h2,body.kata h3,body.kata h4,body.kata h1 span{{letter-spacing:.05em!important}}
  body.kata article.vcase>p.vnote,body.kata .kakite p.kk-d,body.kata .tcard p.tn,body.kata .tcard p.tk,body.kata div.w>p.sh,body.kata .vnav p.vhint,body.kata a>span.tx{{font-size:15px!important;line-height:1.8}}
  body.kata p.src,body.kata ul.srcl>li,body.kata figcaption.zu-cap,body.kata .zu-node small,body.kata p.now,body.kata .kakite p.kk-t{{font-size:13.5px!important}}
  body.kata li>a,body.kata a.ncard span.nn,body.kata p.vans>a.tl,body.kata p.more>a.tl,body.kata p.back>a{{font-size:14px!important}}
  body.kata nav.way li>a{{font-size:12px!important;letter-spacing:0!important;word-break:keep-all;line-height:1.35}}
}}
"""


def block(css):
    return '<style id="sp1121">/* 11/21 スマホの見やすさ（scripts/ippen_sp_1121.py） */' + css + '</style>\n'


def main():
    n_top = n_kata = 0
    for d, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in (".git", "scripts", "node_modules") and not x.startswith("_")]
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            s = open(p, encoding="utf-8").read()
            t = re.sub(r'<style id="sp1121">.*?</style>\n', '', s, flags=re.S)
            rel = os.path.relpath(p, ROOT)
            if rel == "index.html":
                css = TOP
                n_top += 1
            elif re.search(r'<body[^>]*class="[^"]*\bkata\b', t):
                css = KATA
                n_kata += 1
            else:
                css = None
            if css and '</head>' in t:
                t = t.replace('</head>', block(css) + '</head>', 1)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
    print("トップ", n_top, "学校・ガイドの型", n_kata)


if __name__ == "__main__":
    main()
