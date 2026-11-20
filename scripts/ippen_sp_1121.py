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

# 11/21 ちゃん「グラフのところも文字が重なって読みにくい。グラフを横にするとどうかな？少しコンパクトに」
# スマホでは、縦の棒を横の棒にする（左に説明・右に棒、棒の下に金額と「半分戻る」）。のびる動きも横向きに。
KG = """
@media (max-width:700px){
  .kgp .kgs .kg{display:grid;grid-template-columns:1fr;gap:16px;padding:4px 2px 0}
  .kgp .kg li{display:grid;grid-template-columns:142px minmax(0,1fr);grid-template-rows:30px auto auto;column-gap:10px;row-gap:4px;align-items:center;text-align:left}
  .kgp .kg li::before{display:none!important}
  .kgp .kg li:first-child b{grid-row:2}
  .kgp .kg .st{grid-column:1;grid-row:1/4;align-self:start;margin:0;font-size:13px!important;line-height:1.5;word-break:normal!important}
  .kgp .kg .st small{font-size:12px!important;margin-top:2px}
  .kgp .kg li i{grid-column:2;grid-row:1;justify-self:start;align-self:stretch;width:var(--h);height:auto;min-height:0;border-radius:4px 10px 10px 4px;transform-origin:0 50%}
  .kgp .kg li b,.kgp .kg li.main b{position:static;grid-column:2;grid-row:3;justify-self:start;left:auto;right:auto;top:auto;transform:none;font-size:18px;line-height:1.3}
  .kgp .kg li.main b{font-size:21px}
  .kgp .kg li em,.kgp .kg li.main em,.kgp .kg li:nth-child(3) em{position:static;grid-column:2;grid-row:2;justify-self:start;align-self:center;width:auto;padding:2px 9px;border-radius:999px;background:#FA9C88;color:#fff;font-size:12px;line-height:1.5}
  .kgp .kg li em::before{content:"↓ "}
  .kgp.anim[data-s="0"] .kg li:nth-child(1) i,.kgp.anim:is([data-s="0"],[data-s="1"],[data-s="2"]) .kg li:nth-child(2) i,.kgp.anim:is([data-s="0"],[data-s="1"],[data-s="2"],[data-s="3"]) .kg li:nth-child(3) i{transform:scaleX(0)}
  .kg-kami{top:120px}
}
/* 11/21 ちゃん「スマホ、いまの特典は横スライドにするといいかな」 */
@media (max-width:700px){
  ul.tix{display:flex!important;flex-wrap:nowrap!important;gap:12px!important;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain;align-items:stretch!important;margin:14px 0 0!important;padding:4px 2px 14px!important;scrollbar-width:none}
  ul.tix::-webkit-scrollbar{display:none}
  ul.tix>li{flex:0 0 82%!important;max-width:82%!important;height:auto!important;min-height:0!important;margin:0!important;scroll-snap-align:start;display:flex!important;flex-direction:column;align-items:center}
  ul.tix>li>*{width:100%}
  .tix-h::after{content:"横にスライドすると、ほかの学校の特典も見られます →";display:block;margin-top:6px;font-size:13px;font-weight:400;letter-spacing:.03em;color:var(--sub)}
}
"""

# 11/21 ちゃん「吹き出しが左揃えでバランスが悪い。吹き出しの中いっぱいに文字を」
# 「本文のどのテキストも左揃えになってる。端から端まで文章をおいて、みやすいように」
# スマホでは、左揃えの本文（20字より長いもの）を両端揃えにし、文節でしか折らない決まりをゆるめて行の端まで置く。
# まん中揃えにしてある所はさわらない（見た目で左揃えのものだけに印をつける）。
ALLP = """
@media (max-width:700px){
  .sp-j{text-align:justify!important;text-justify:inter-character;word-break:normal!important;overflow-wrap:normal!important;line-break:normal}
  .sp-j wbr{display:none}
  .kg-talk .say:not(.jk),.kg-moz .say{width:max-content!important;text-align:left!important}
  .kg-moz .say br{display:inline!important}
  .kg-moz .say .pc{display:inline!important}.kg-moz .say .sp{display:none!important}
}
</style><script>(function(){if(!matchMedia('(max-width:700px)').matches)return;function f(){var q=document.querySelectorAll('p,li,dd,blockquote,figcaption');for(var i=0;i<q.length;i++){var e=q[i],a=getComputedStyle(e).textAlign;if((a==='start'||a==='left')&&e.textContent.replace(/\\s/g,'').length>20&&e.clientWidth>250&&parseFloat(getComputedStyle(e).fontSize)<17.5&&!e.closest('nav,header,footer,.crumb,table,.kgp'))e.classList.add('sp-j')}}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',f);else f()})();</script><style>
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
    # 終わりの印 sp1121-end まで1まとまり（中に script をはさむため）
    return ('<style id="sp1121">/* 11/21 スマホの見やすさ（scripts/ippen_sp_1121.py） */' + css + ALLP
            + '</style><!--sp1121-end-->\n')


def main():
    n_top = n_kata = n_other = 0
    for d, ds, fs in os.walk(ROOT):
        ds[:] = [x for x in ds if x not in (".git", "scripts", "node_modules") and not x.startswith("_")]
        for f in fs:
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            s = open(p, encoding="utf-8").read()
            t = re.sub(r'<style id="sp1121">.*?</style><!--sp1121-end-->\n', '', s, flags=re.S)
            t = re.sub(r'<style id="sp1121">.*?</style>\n', '', t, flags=re.S)
            rel = os.path.relpath(p, ROOT)
            if rel == "index.html":
                css = TOP + KG
                n_top += 1
            elif re.search(r'<body[^>]*class="[^"]*\bkata\b', t):
                css = KATA
                n_kata += 1
            else:
                css = ""
                n_other += 1
            if '</head>' in t and '<html' in t[:500].lower() + t.lower()[:2000]:
                t = t.replace('</head>', block(css) + '</head>', 1)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
    print("トップ", n_top, "学校・ガイドの型", n_kata, "そのほか", n_other)


if __name__ == "__main__":
    main()
