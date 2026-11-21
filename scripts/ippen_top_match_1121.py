#!/usr/bin/env python3
"""11/21 トップの「いまのあなたは？」を、悩み顔の5人から「モヤン＋言葉の一覧」に変え、押すと1校だけ出す。

ちゃん（意見をもらって）「画像の選択肢を選んだ時に出てくる商品は一つの方がいい。読者が悩んでしまう。
その悩みを1番解決する商品へ案内できると最高」→ ラフ 案C8（picnic-docs/1108_サイトの設計/イメージ/ラフ_1121_悩みの人の置き場所/）でOK。
- 5人の絵をやめ、モヤン（右）が「わたしは、どれに近いかな？」と聞く。5つは白い丸のアイコン＋言葉の一覧
- 押すと、サイトの数字で選んだ1校だけを出す（費用・土日→地域連携PF／夜・振替→LEC／迷い→6校くらべ）
何回かけても同じ（<style id="match1121"> と印 match1121 で入れかえる）。
使い方：python3 scripts/ippen_top_match_1121.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOP = ROOT / "index.html"

ITEMS = [
    ("cost", "img/top/fuan_okane.webp", "できるだけ、<br>費用をおさえたい", ""),
    ("donichi", "img/top/fuan_tsuzuku.webp", "土日に受けたい", ""),
    ("yoru", "img/top/nayami_yoru.webp", "仕事のあと、<br>平日の夜に受けたい", ""),
    ("support", "img/top/nayami_furikae.webp", "休んでも、<br>振替できる所にしたい", ""),
    ("mada", "img/top/nayami_mada.webp", "たくさんあって、<br>まだ迷っている", " r5-wide"),
]


def block():
    bt = "".join(
        f'<button class="r5-c{w}" type="button" data-k="{k}" data-ev="top_match_{k}" aria-pressed="false">'
        f'<span class="r5-i"><img loading="lazy" decoding="async" src="{src}" alt=""></span>'
        f'<span class="r5-t">{txt}</span></button>'
        for k, src, txt, w in ITEMS)
    return ('<!--match1121--><div class="r5">'
            '<div class="r5-mo"><img loading="lazy" decoding="async" src="img/parts/t/moyan_school_hat_smile-200.webp" alt="">'
            '<p class="r5-say">わたしは、どれに近いかな？</p></div>'
            f'<div class="r5-list" role="group" aria-label="いまのあなた">{bt}</div></div><!--/match1121-->')


CSS = """<style id="match1121">
.r5{max-width:600px;margin:22px auto 0}
.r5-mo{display:flex;flex-direction:row-reverse;align-items:center;justify-content:center;gap:14px;margin-bottom:22px}
.r5-mo img{width:92px;height:auto;filter:drop-shadow(0 2px 3px rgba(46,74,120,.18))}
.r5-say{position:relative;margin:0;padding:12px 18px;background:#fff;border-radius:16px;font-size:16px;font-weight:700;color:var(--ink)}
.r5-say::before{content:"";position:absolute;right:-7px;top:50%;width:14px;height:14px;margin-top:-7px;background:#fff;transform:rotate(45deg)}
.r5-list{display:flex;flex-direction:column;border-top:1.5px dashed rgba(46,74,120,.25)}
.r5-c{display:flex;align-items:center;gap:24px;width:100%;padding:16px 10px;border:0;border-bottom:1.5px dashed rgba(46,74,120,.25);border-radius:0;background:none;font:inherit;color:var(--ink);cursor:pointer;text-align:left}
.r5-c::after{content:"›";margin-left:auto;font-size:26px;font-weight:700;color:#FA9C88}
.r5-c[aria-pressed="true"]{background:#FFF7F2}
@media (hover:hover){.r5-c:hover{background:#FFF7F2}}
.r5-i{flex:none;display:grid;place-items:center;width:64px;height:64px;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(46,74,120,.10)}
.r5-i img{display:block;width:46px;height:46px;object-fit:contain}
.r5-t{font-size:18px;font-weight:700;color:#1F3354;letter-spacing:.02em;line-height:1.5}
.r5-t br{display:none}
.r5-c[aria-pressed="true"] .r5-t{color:#D9604A}
#sel-res{background:none;padding:0;box-shadow:none;border:0}
.one{max-width:520px;margin:18px auto 0;padding:20px 22px;background:#fff;border-radius:18px;text-align:center;box-shadow:0 2px 0 rgba(46,74,120,.08)}
.one-k{margin:0 0 4px;font-size:13.5px;color:var(--sub)}
.one-h{margin:0;font-size:21px;font-weight:700;color:var(--ink)}
.one-h .pr{margin-left:8px;vertical-align:middle}
.one-why{margin:8px 0 14px;font-size:15px;line-height:1.7}
.one-go{display:inline-block;padding:12px 26px;border-radius:999px;background:#FA9C88;color:#fff!important;font-weight:700;text-decoration:none}
@media (max-width:700px){
  .r5-mo img{width:70px}
  .r5-c{gap:18px;padding:14px 6px}
  .r5-i{width:54px;height:54px}
  .r5-i img{width:40px;height:40px}
  .r5-t{font-size:16.5px!important;word-break:keep-all;overflow-wrap:anywhere}
  .r5-t br{display:inline}
  .one{padding:18px 16px}
  .one-h{font-size:19px}
}
</style>
"""

M_JS = """  var M = {
    cost:['chiiki','6校でいちばん安い（総額297,000円）'],
    donichi:['chiiki','土日のクラスがあって、6校でいちばん安い'],
    yoru:['lec','平日夜と半日のクラスあり。休んでも振替が回数の制限なし・無料'],
    support:['lec','振替が回数の制限なし・無料。同じ条件の学校より総額が66,000円安い'],
    mada:'compare'
  };
"""
SHOW_JS = """  function show(k){
    var m = M[k], h = '';
    if (m === 'compare') {
      h = '<div class="one"><p class="one-h">まずは、6校をひと目でくらべてみてね</p><p class="one-why">費用・受けられる日・振替を、1つの表に並べました。</p><a class="one-go" href="/schools/compare/" data-ev="top_match_go_compare">6校くらべを見る</a></div>';
    } else {
      var s = S[m[0]], ext = /^https?:/.test(s.h);
      h = '<div class="one"><p class="one-k">いまのあなたに、いちばん合うのは</p><p class="one-h">' + s.n + (s.pr ? '<span class="pr">PR</span>' : '') + '</p><p class="one-why">' + m[1] + '</p><a class="one-go" href="' + s.h + '" data-ev="top_match_go_' + m[0] + '"' + (ext ? ' target="_blank" rel="noopener"' : '') + '>くわしく見る</a></div>';
    }
    res.innerHTML = h;
  }
"""


def main():
    t = TOP.read_text(encoding="utf-8")
    s = t
    # 1. 5人 → モヤン＋一覧
    if "<!--match1121-->" in t:
        t = re.sub(r"<!--match1121-->.*?<!--/match1121-->", block(), t, count=1, flags=re.S)
    else:
        i = t.index('<div class="people"')
        j = t.index('<div class="res" id="sel-res"', i)
        t = t[:i] + block() + "\n        " + t[j:]
    t = t.replace("<small>気持ちが近い人を、押してみてね</small>", "<small>近いものを、押してみてね</small>", 1)
    # 2. 押したときの中身（1校だけ）
    a = t.index("  var M = {")
    b = t.index("  var ps = ", a)
    t = t[:a] + M_JS + t[b:]
    a = t.index("  function show(k){")
    b = t.index("  ps.forEach(", a)
    t = t[:a] + SHOW_JS + t[b:]
    t = t.replace("document.querySelectorAll('.person'), res", "document.querySelectorAll('.r5-c'), res", 1)
    # 3. 見た目
    t = re.sub(r'<style id="match1121">.*?</style>\n', "", t, flags=re.S)
    t = t.replace("</head>", CSS + "</head>", 1)
    assert "querySelectorAll('.r5-c'), res" in t
    if t != s:
        TOP.write_text(t, encoding="utf-8")
    print("ok", t.count('class="r5-c'))


if __name__ == "__main__":
    main()
